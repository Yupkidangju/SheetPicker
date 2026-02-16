"""
[v2.0.0] 검색 인덱스 엔진
Inverted Index, 초성 인덱스, BM25 인덱스를 구축하여 고속 검색을 지원합니다.
파일 로드 시 1회 인덱싱하면 이후 검색은 O(1)~O(n) 수준으로 수행됩니다.
"""

import re
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict
from src.core.jamo_utils import extract_chosung, is_hangul_syllable

try:
    from rank_bm25 import BM25Okapi
except ImportError:
    BM25Okapi = None


@dataclass
class CellInfo:
    """개별 셀 정보를 저장하는 데이터 클래스"""
    file_path: str
    file_name: str
    sheet_name: str
    row_idx: int
    col_idx: int
    col_name: str
    value: str


@dataclass
class RowData:
    """행 단위 데이터를 저장하는 데이터 클래스"""
    file_path: str
    file_name: str
    sheet_name: str
    row_idx: int
    cells: Dict[str, str]
    headers: List[str]


class SearchIndex:
    """
    [v2.0.0] 다중 계층 검색 인덱스.
    - inverted_index: 정규화된 토큰 → 셀 인덱스 집합 (정확/부분 매칭용)
    - chosung_index: 초성 문자열 → 셀 인덱스 집합 (초성 검색용)
    - vocabulary: 고유 토큰 집합 (퍼지 매칭 대상)
    - bm25: BM25 랭킹 인스턴스 (관련도 순위용)
    """

    def __init__(self):
        # 셀 데이터 저장소
        self.cells: List[CellInfo] = []
        # 행 데이터 저장소: (file_path, sheet_name, row_idx) → RowData
        self.rows: Dict[Tuple[str, str, int], RowData] = {}
        # 시트별 헤더 정보
        self.file_headers: Dict[Tuple[str, str], List[str]] = {}

        # 검색 인덱스들
        self.inverted_index: Dict[str, Set[int]] = defaultdict(set)
        self.chosung_index: Dict[str, Set[int]] = defaultdict(set)
        self.vocabulary: Set[str] = set()

        # BM25 관련
        self._bm25: Optional[object] = None
        self._bm25_row_keys: List[Tuple[str, str, int]] = []
        self._bm25_dirty = True

        # 파일 관리
        self._indexed_files: Set[str] = set()

    @property
    def total_cells(self) -> int:
        return len(self.cells)

    @property
    def total_rows(self) -> int:
        return len(self.rows)

    @property
    def total_files(self) -> int:
        return len(self._indexed_files)

    @property
    def indexed_files(self) -> Set[str]:
        return self._indexed_files.copy()

    def clear(self):
        """인덱스 전체 초기화"""
        self.__init__()

    def add_dataframe(self, file_path: str, file_name: str,
                      sheet_name: str, df, row_offset: int = 0):
        """
        DataFrame을 인덱스에 추가합니다.
        scanner에서 전달받은 chunk 데이터를 처리합니다.

        Args:
            file_path: 파일 전체 경로
            file_name: 파일명
            sheet_name: 시트명
            df: pandas DataFrame
            row_offset: 청크 처리 시 행 인덱스 오프셋
        """
        headers = [str(col) for col in df.columns]
        header_key = (file_path, sheet_name)
        if header_key not in self.file_headers:
            self.file_headers[header_key] = headers

        self._indexed_files.add(file_path)
        self._bm25_dirty = True

        for local_idx, (_, row) in enumerate(df.iterrows()):
            actual_row_idx = row_offset + local_idx
            row_key = (file_path, sheet_name, actual_row_idx)
            cells_dict = {}

            for col_idx, col_name in enumerate(headers):
                raw_val = row.iloc[col_idx] if col_idx < len(row) else None
                value = str(raw_val) if raw_val is not None else ''

                # NaN, None 등 무효값 건너뛰기
                if value in ('nan', 'None', 'NaT', ''):
                    continue

                cells_dict[col_name] = value

                # 셀 정보 저장
                cell_info = CellInfo(
                    file_path=file_path,
                    file_name=file_name,
                    sheet_name=sheet_name,
                    row_idx=actual_row_idx,
                    col_idx=col_idx,
                    col_name=col_name,
                    value=value
                )
                cell_idx = len(self.cells)
                self.cells.append(cell_info)

                # 정규화 후 인버티드 인덱스에 추가
                normalized = value.lower().strip()
                tokens = self._tokenize(normalized)
                for token in tokens:
                    self.inverted_index[token].add(cell_idx)
                    self.vocabulary.add(token)

                # 한글이 포함된 경우 초성 인덱스에도 추가
                if any(is_hangul_syllable(c) for c in value):
                    chosung_str = extract_chosung(value)
                    chosung_tokens = self._tokenize(chosung_str.lower())
                    for ct in chosung_tokens:
                        self.chosung_index[ct].add(cell_idx)

            # 행 데이터 저장 (유효한 셀이 있는 경우만)
            if cells_dict:
                self.rows[row_key] = RowData(
                    file_path=file_path,
                    file_name=file_name,
                    sheet_name=sheet_name,
                    row_idx=actual_row_idx,
                    cells=cells_dict,
                    headers=headers
                )

    def remove_file(self, file_path: str):
        """파일을 인덱스에서 제거하고 관련 데이터를 정리합니다."""
        # 제거할 셀 인덱스 수집
        remove_indices = {
            i for i, c in enumerate(self.cells)
            if c is not None and c.file_path == file_path
        }
        if not remove_indices:
            return

        # 인버티드 인덱스에서 제거
        empty_keys = []
        for key, idx_set in self.inverted_index.items():
            idx_set -= remove_indices
            if not idx_set:
                empty_keys.append(key)
        for key in empty_keys:
            del self.inverted_index[key]
            self.vocabulary.discard(key)

        # 초성 인덱스에서 제거
        empty_keys = []
        for key, idx_set in self.chosung_index.items():
            idx_set -= remove_indices
            if not idx_set:
                empty_keys.append(key)
        for key in empty_keys:
            del self.chosung_index[key]

        # 셀 데이터 무효화 (인덱스 순서 유지를 위해 None 처리)
        for i in remove_indices:
            self.cells[i] = None

        # 행 데이터 제거
        row_keys_to_remove = [k for k in self.rows if k[0] == file_path]
        for k in row_keys_to_remove:
            del self.rows[k]

        # 헤더 제거
        header_keys_to_remove = [k for k in self.file_headers if k[0] == file_path]
        for k in header_keys_to_remove:
            del self.file_headers[k]

        self._indexed_files.discard(file_path)
        self._bm25_dirty = True

    def build_bm25(self):
        """BM25 인덱스를 (재)구축합니다. 행 단위로 토큰화하여 관련도 랭킹에 사용."""
        if BM25Okapi is None:
            return

        corpus = []
        self._bm25_row_keys = []

        for row_key, row_data in self.rows.items():
            # 행의 모든 셀 값을 결합하여 하나의 "문서"로 취급
            row_text = ' '.join(row_data.cells.values()).lower()
            tokens = row_text.split()
            corpus.append(tokens)
            self._bm25_row_keys.append(row_key)

        if corpus:
            self._bm25 = BM25Okapi(corpus)
        self._bm25_dirty = False

    def get_bm25_scores(self, query: str) -> Dict[Tuple, float]:
        """BM25 기반 관련도 점수를 반환합니다."""
        if self._bm25_dirty:
            self.build_bm25()

        if self._bm25 is None or not self._bm25_row_keys:
            return {}

        tokens = query.lower().split()
        scores = self._bm25.get_scores(tokens)

        result = {}
        for i, score in enumerate(scores):
            if score > 0:
                result[self._bm25_row_keys[i]] = float(score)
        return result

    def _tokenize(self, text: str) -> Set[str]:
        """텍스트를 검색용 토큰으로 분리합니다."""
        tokens = set()
        if not text:
            return tokens
        # 전체 텍스트 자체도 토큰으로 추가 (완전 일치용)
        tokens.add(text)
        # 구두점/공백 기준 단어 분리
        words = re.split(r'[\s,;|/\\()\[\]{}<>:\"\']+', text)
        for w in words:
            w = w.strip()
            if w and len(w) > 0:
                tokens.add(w)
        return tokens

    def find_cells_containing(self, keyword: str) -> Set[int]:
        """
        키워드를 포함하는 셀 인덱스를 반환합니다.
        인버티드 인덱스의 토큰 중 키워드를 포함하는 토큰의 셀들을 합산합니다.
        """
        keyword_lower = keyword.lower().strip()
        if not keyword_lower:
            return set()

        result = set()
        # 정확한 토큰 매칭 (O(1))
        if keyword_lower in self.inverted_index:
            result.update(self.inverted_index[keyword_lower])

        # 부분 문자열 매칭 (토큰 순회)
        for token, cell_indices in self.inverted_index.items():
            if token != keyword_lower and keyword_lower in token:
                result.update(cell_indices)

        return result

    def find_cells_by_chosung(self, chosung_query: str) -> Set[int]:
        """초성 쿼리로 매칭되는 셀 인덱스를 반환합니다."""
        query_lower = chosung_query.lower().strip()
        if not query_lower:
            return set()

        result = set()
        for token, cell_indices in self.chosung_index.items():
            if query_lower in token:
                result.update(cell_indices)
        return result

    def cell_to_row_key(self, cell_idx: int) -> Optional[Tuple[str, str, int]]:
        """셀 인덱스로부터 행 키를 추출합니다."""
        cell = self.cells[cell_idx]
        if cell is None:
            return None
        return (cell.file_path, cell.sheet_name, cell.row_idx)
