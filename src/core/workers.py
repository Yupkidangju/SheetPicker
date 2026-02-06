from PySide6.QtCore import QThread, Signal, QObject
from typing import List
from pathlib import Path
from src.core.scanner import FileScanner
from src.core.searcher import DataSearcher
from src.utils.logger import logger

class SearchWorker(QThread):
    """
    [KR] 검색 작업을 수행하는 백그라운드 워커 스레드.
    UI 프리징을 방지하기 위해 별도 스레드에서 파일 로딩 및 검색을 수행합니다.
    """

    # [KR] Signals
    result_found = Signal(list)   # 검색 결과 발견 시 방출 (List[dict])
    progress_updated = Signal(str) # 진행 상태 메시지
    error_occurred = Signal(str)   # 에러 발생 시 방출
    finished_task = Signal()       # 작업 완료 시 방출 (finished는 QThread 기본 시그널과 겹치므로 이름 변경)

    def __init__(self, files: List[str], keyword: str, by_column: bool, case_sensitive: bool, use_regex: bool = False):
        super().__init__()
        self.files = files
        self.keyword = keyword
        self.by_column = by_column
        self.case_sensitive = case_sensitive
        self.use_regex = use_regex
        self.target_columns = None # [KR] 컬럼 타겟팅을 위한 속성 (외부 주입)
        self.scanner = FileScanner()
        self._is_running = True

    def run(self):
        """
        [KR] 스레드 실행 진입점.
        """
        logger.info(f"Worker started. Keyword: '{self.keyword}', Files: {len(self.files)}")
        self.progress_updated.emit(f"Starting search for '{self.keyword}'...")

        for file_path in self.files:
            if not self._is_running:
                logger.info("Search aborted by user.")
                break

            file_name = Path(file_path).name
            self.progress_updated.emit(f"Scanning: {file_name}")
            logger.debug(f"Scanning file: {file_path}")

            try:
                # [KR] Chunk 단위로 파일 읽기
                for chunk_info in self.scanner.read_file_chunks(file_path):
                    if not self._is_running:
                        break

                    sheet_name = chunk_info['sheet_name']
                    df = chunk_info['data']

                    # [KR] 검색 수행
                    results_df = DataSearcher.search_dataframe(
                        df,
                        self.keyword,
                        by_column=self.by_column,
                        case_sensitive=self.case_sensitive,
                        use_regex=self.use_regex,
                        target_columns=self.target_columns
                    )

                    # [KR] 결과가 있으면 UI로 전송
                    if not results_df.empty:
                        batch_results = []
                        columns = results_df.columns
                        for row in results_df.itertuples(index=False, name=None):
                            # Preview 텍스트 생성
                            preview = DataSearcher.format_result_row(row)

                            result_data = {
                                'file': file_name,
                                'full_path': str(file_path),
                                'sheet': sheet_name,
                                'preview': preview,
                                'raw_data': dict(zip(columns, row))
                            }
                            batch_results.append(result_data)

                            # [KR] Batch Emission (100개 단위)
                            if len(batch_results) >= 100:
                                self.result_found.emit(batch_results)
                                batch_results = []

                        # [KR] 남은 결과 방출
                        if batch_results:
                            self.result_found.emit(batch_results)

            except Exception as e:
                # [KR] 개별 파일 에러는 전체 프로세스를 중단하지 않고 로그만 남김
                logger.error(f"Error processing {file_name}: {e}", exc_info=True)
                self.error_occurred.emit(f"Error reading {file_name}: {str(e)}")

        self.progress_updated.emit("Search completed.")
        self.finished_task.emit()
        logger.info("Worker finished task.")

    def stop(self):
        """
        [KR] 작업 중단 요청
        """
        self._is_running = False
