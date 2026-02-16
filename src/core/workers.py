"""
[v2.0.0] 백그라운드 워커 스레드
인덱싱과 검색을 별도 스레드에서 수행하여 GUI 프리징을 방지합니다.
"""

from PySide6.QtCore import QThread, Signal
from typing import List
from pathlib import Path
from src.core.scanner import FileScanner
from src.core.indexer import SearchIndex
from src.core.searcher import MultiLayerSearcher, SearchResult
from src.core.cache import IndexCache
from src.utils.logger import logger


class IndexWorker(QThread):
    """
    [v2.0.0] 파일 인덱싱 워커.
    파일을 스캔하고 SearchIndex를 구축합니다.
    SQLite 캐시가 유효한 경우 파일을 다시 읽지 않고 캐시에서 복원합니다.
    """

    # 시그널 정의
    progress_updated = Signal(str, int)   # (메시지, 백분율)
    indexing_complete = Signal(int, int)   # (총 파일 수, 총 행 수)
    error_occurred = Signal(str)           # 에러 메시지

    def __init__(self, files: List[str], index: SearchIndex,
                 cache: IndexCache = None):
        super().__init__()
        self.files = files
        self.index = index
        self.cache = cache
        self.scanner = FileScanner()
        self._is_running = True

    def run(self):
        """인덱싱 작업 수행"""
        logger.info(f"인덱싱 시작: {len(self.files)}개 파일")
        total = len(self.files)

        for i, file_path in enumerate(self.files):
            if not self._is_running:
                logger.info("인덱싱 중단됨 (사용자 요청)")
                break

            file_name = Path(file_path).name
            pct = int(((i) / max(total, 1)) * 100)
            self.progress_updated.emit(f"인덱싱 중: {file_name}", pct)

            # 이미 인덱싱된 파일은 건너뛰기
            if file_path in self.index.indexed_files:
                continue

            try:
                # 캐시 확인 — 캐시가 유효하면 파일을 다시 읽지 않음
                if self.cache and self.cache.is_file_cached(file_path):
                    cached = self.cache.load_file_data(file_path)
                    if cached:
                        self._restore_from_cache(cached)
                        logger.info(f"캐시에서 복원: {file_name}")
                        continue

                # 파일에서 직접 로드 + 인덱싱
                cells_for_cache = []
                headers_for_cache = {}
                row_offset = 0

                for chunk_info in self.scanner.read_file_chunks(file_path):
                    if not self._is_running:
                        break

                    sheet_name = chunk_info['sheet_name']
                    df = chunk_info['data']
                    headers = [str(c) for c in df.columns]

                    # 인덱스에 추가
                    self.index.add_dataframe(
                        file_path, file_name, sheet_name, df, row_offset
                    )

                    # 캐시용 데이터 수집
                    if self.cache:
                        if sheet_name not in headers_for_cache:
                            headers_for_cache[sheet_name] = headers
                        for local_idx, (_, row) in enumerate(df.iterrows()):
                            actual_row = row_offset + local_idx
                            for col_idx, col_name in enumerate(headers):
                                val = row.iloc[col_idx] if col_idx < len(row) else None
                                val_str = str(val) if val is not None else ''
                                if val_str not in ('nan', 'None', 'NaT', ''):
                                    cells_for_cache.append({
                                        'file_path': file_path,
                                        'file_name': file_name,
                                        'sheet_name': sheet_name,
                                        'row_idx': actual_row,
                                        'col_idx': col_idx,
                                        'col_name': col_name,
                                        'value': val_str
                                    })

                    row_offset += len(df)

                # 캐시에 저장
                if self.cache and cells_for_cache:
                    self.cache.save_file_data(
                        file_path, file_name, cells_for_cache, headers_for_cache
                    )

            except Exception as e:
                err_msg = f"인덱싱 실패: {file_name} — {str(e)}"
                logger.error(err_msg, exc_info=True)
                self.error_occurred.emit(err_msg)

        # BM25 인덱스 구축
        if self._is_running:
            self.progress_updated.emit("BM25 인덱스 구축 중...", 95)
            self.index.build_bm25()

        self.progress_updated.emit("인덱싱 완료", 100)
        self.indexing_complete.emit(self.index.total_files, self.index.total_rows)
        logger.info(
            f"인덱싱 완료: {self.index.total_files}개 파일, "
            f"{self.index.total_rows}개 행, {self.index.total_cells}개 셀"
        )

    def _restore_from_cache(self, cached: dict):
        """캐시 데이터로부터 인덱스를 복원합니다."""
        import pandas as pd
        from collections import defaultdict

        file_path = cached['file_path']
        file_name = cached['file_name']
        headers_map = cached['headers']

        # 셀 데이터를 시트별/행별로 그룹핑하여 DataFrame으로 변환
        sheets_data = defaultdict(lambda: defaultdict(dict))
        for cell in cached['cells']:
            sheet = cell['sheet_name']
            row_idx = cell['row_idx']
            col_name = cell['col_name']
            sheets_data[sheet][row_idx][col_name] = cell['value']

        for sheet_name, rows in sheets_data.items():
            headers = headers_map.get(sheet_name, [])
            if not headers:
                continue

            # 행 데이터를 DataFrame으로 변환
            df_data = []
            row_indices = sorted(rows.keys())
            for row_idx in row_indices:
                row_dict = rows[row_idx]
                df_row = {h: row_dict.get(h, '') for h in headers}
                df_data.append(df_row)

            if df_data:
                df = pd.DataFrame(df_data, columns=headers)
                min_row = min(row_indices)
                self.index.add_dataframe(
                    file_path, file_name, sheet_name, df, min_row
                )

    def stop(self):
        """인덱싱 중단 요청"""
        self._is_running = False


class SearchWorker(QThread):
    """
    [v2.0.0] 검색 워커.
    다중 계층 검색을 백그라운드에서 수행합니다.
    """

    results_ready = Signal(list)    # List[SearchResult]
    search_error = Signal(str)
    search_time = Signal(float)     # 검색 소요 시간 (초)

    def __init__(self, query_text: str, index: SearchIndex,
                 min_similarity: float = 0.6):
        super().__init__()
        self.query_text = query_text
        self.index = index
        self.min_similarity = min_similarity

    def run(self):
        """검색 수행"""
        import time
        start = time.perf_counter()

        try:
            searcher = MultiLayerSearcher(self.index)
            results = searcher.search(
                self.query_text,
                min_similarity=self.min_similarity
            )
            elapsed = time.perf_counter() - start

            self.results_ready.emit(results)
            self.search_time.emit(elapsed)

            logger.info(
                f"검색 완료: '{self.query_text}' → {len(results)}건 ({elapsed:.3f}초)"
            )
        except Exception as e:
            logger.error(f"검색 오류: {e}", exc_info=True)
            self.search_error.emit(str(e))
