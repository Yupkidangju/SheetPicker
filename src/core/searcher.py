"""
[v2.0.0] 다중 계층 검색 엔진
쿼리 파싱, 정확 매칭, 퍼지 매칭, 초성 검색, BM25 랭킹을 통합하여
사용자가 단순히 텍스트를 입력하면 최적의 결과를 반환합니다.
"""

import re
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Set, Optional
from src.core.indexer import SearchIndex, RowData
from src.core.jamo_utils import is_chosung_query, match_chosung, extract_chosung
from src.utils.logger import logger

try:
    from rapidfuzz import fuzz, process as rfprocess
    HAS_RAPIDFUZZ = True
except ImportError:
    HAS_RAPIDFUZZ = False
    logger.warning("rapidfuzz 미설치 — 퍼지 매칭 비활성화")


@dataclass
class SearchQuery:
    """파싱된 검색 쿼리"""
    keywords: List[str]       # 일반 검색어 (AND 조건)
    excludes: List[str]       # 제외 검색어 ('-' 접두사)
    ranges: List[Tuple[float, float]]  # 숫자 범위 (min~max)
    raw: str                  # 원본 검색 문자열


@dataclass
class MatchDetail:
    """개별 매칭 상세 정보"""
    col_name: str
    cell_value: str
    match_type: str    # 'exact', 'fuzzy', 'chosung', 'range'
    similarity: float  # 0.0 ~ 1.0


@dataclass
class SearchResult:
    """검색 결과 단위 (행 기준)"""
    row: RowData
    score: float              # 종합 점수
    match_type: str           # 최우선 매칭 유형
    similarity: float         # 최고 유사도
    matches: List[MatchDetail] = field(default_factory=list)


class QueryParser:
    """
    검색어를 파싱하여 구조화된 쿼리 객체로 변환합니다.

    규칙:
    - 공백 = AND 조건 (여러 키워드 동시 포함)
    - '-키워드' = 제외 조건
    - '숫자~숫자' = 범위 검색
    - 그 외 = 일반 키워드
    """

    # 숫자 범위 패턴: 100~500, 10000~50000 등
    RANGE_PATTERN = re.compile(r'^(\d+(?:\.\d+)?)\s*[~\-]\s*(\d+(?:\.\d+)?)$')

    @staticmethod
    def parse(raw_query: str) -> SearchQuery:
        """원시 검색어를 SearchQuery로 파싱합니다."""
        keywords = []
        excludes = []
        ranges = []

        if not raw_query or not raw_query.strip():
            return SearchQuery(keywords=[], excludes=[], ranges=[], raw=raw_query or '')

        tokens = raw_query.strip().split()

        for token in tokens:
            # 제외 검색어 처리
            if token.startswith('-') and len(token) > 1:
                excludes.append(token[1:])
                continue

            # 범위 검색 처리
            range_match = QueryParser.RANGE_PATTERN.match(token)
            if range_match:
                min_val = float(range_match.group(1))
                max_val = float(range_match.group(2))
                if min_val > max_val:
                    min_val, max_val = max_val, min_val
                ranges.append((min_val, max_val))
                continue

            # 일반 키워드
            keywords.append(token)

        return SearchQuery(
            keywords=keywords,
            excludes=excludes,
            ranges=ranges,
            raw=raw_query
        )


class MultiLayerSearcher:
    """
    [v2.0.0] 다중 계층 검색 엔진.
    4가지 검색 알고리즘을 동시에 실행하고 점수를 합산하여 최적 결과를 반환합니다.

    계층 1: 정확 매칭 (Inverted Index) — 가중치 1.0
    계층 2: 초성 검색 (Jamo Index) — 가중치 0.85
    계층 3: 퍼지 매칭 (rapidfuzz) — 가중치 × 유사도
    계층 4: BM25 랭킹 — 관련도 가산점
    """

    # 검색 계층별 기본 가중치
    WEIGHT_EXACT = 1.0
    WEIGHT_CHOSUNG = 0.85
    WEIGHT_FUZZY = 0.7
    WEIGHT_BM25 = 0.3
    WEIGHT_RANGE = 0.9

    def __init__(self, index: SearchIndex):
        self.index = index

    def search(self, raw_query: str, min_similarity: float = 0.6,
               max_results: int = 500) -> List[SearchResult]:
        """
        검색을 실행하고 점수순으로 정렬된 결과를 반환합니다.

        Args:
            raw_query: 사용자 입력 검색어
            min_similarity: 퍼지 매칭 최소 유사도 (0.0~1.0)
            max_results: 최대 결과 수
        """
        query = QueryParser.parse(raw_query)

        if not query.keywords and not query.ranges:
            return []

        # 행 키 → {score, match_type, similarity, matches} 누적 딕셔너리
        row_scores: Dict[Tuple, dict] = {}

        # 각 키워드에 대해 다중 계층 검색 수행
        for keyword in query.keywords:
            # 계층 1: 정확 매칭
            self._exact_search(keyword, row_scores)

            # 계층 2: 초성 검색 (입력이 초성인 경우)
            if is_chosung_query(keyword):
                self._chosung_search(keyword, row_scores)

            # 계층 3: 퍼지 매칭
            if HAS_RAPIDFUZZ:
                self._fuzzy_search(keyword, row_scores, min_similarity)

        # 범위 검색
        for min_val, max_val in query.ranges:
            self._range_search(min_val, max_val, row_scores)

        # 계층 4: BM25 관련도 점수 가산
        if query.keywords:
            bm25_query = ' '.join(query.keywords)
            self._apply_bm25(bm25_query, row_scores)

        # 제외 조건 적용
        if query.excludes:
            self._apply_excludes(query.excludes, row_scores)

        # AND 조건 적용: 모든 키워드가 행에 포함되어야 함 (2개 이상일 때)
        if len(query.keywords) > 1:
            self._apply_and_condition(query.keywords, row_scores)

        # 결과 생성 및 정렬
        results = []
        for row_key, info in row_scores.items():
            row_data = self.index.rows.get(row_key)
            if row_data is None:
                continue
            results.append(SearchResult(
                row=row_data,
                score=info['score'],
                match_type=info['match_type'],
                similarity=info['similarity'],
                matches=info.get('matches', [])
            ))

        # 점수 내림차순 정렬
        results.sort(key=lambda r: r.score, reverse=True)
        return results[:max_results]

    def _exact_search(self, keyword: str, row_scores: dict):
        """계층 1: 인버티드 인덱스 기반 정확/부분 매칭"""
        cell_indices = self.index.find_cells_containing(keyword)

        for cell_idx in cell_indices:
            cell = self.index.cells[cell_idx]
            if cell is None:
                continue

            row_key = (cell.file_path, cell.sheet_name, cell.row_idx)

            # 완전 일치 vs 부분 일치 구분
            val_lower = cell.value.lower()
            kw_lower = keyword.lower()
            if val_lower == kw_lower:
                sim = 1.0
            else:
                sim = 0.9 if kw_lower in val_lower else 0.8

            score = self.WEIGHT_EXACT * sim
            match = MatchDetail(
                col_name=cell.col_name,
                cell_value=cell.value,
                match_type='exact',
                similarity=sim
            )
            self._update_row_score(row_scores, row_key, score, 'exact', sim, match)

    def _chosung_search(self, keyword: str, row_scores: dict):
        """계층 2: 한글 초성 인덱스 기반 검색"""
        cell_indices = self.index.find_cells_by_chosung(keyword)

        for cell_idx in cell_indices:
            cell = self.index.cells[cell_idx]
            if cell is None:
                continue

            row_key = (cell.file_path, cell.sheet_name, cell.row_idx)

            # 초성 유사도 계산
            text_chosung = extract_chosung(cell.value)
            if keyword in text_chosung:
                sim = 0.85
            else:
                sim = 0.7

            score = self.WEIGHT_CHOSUNG * sim
            match = MatchDetail(
                col_name=cell.col_name,
                cell_value=cell.value,
                match_type='chosung',
                similarity=sim
            )
            self._update_row_score(row_scores, row_key, score, 'chosung', sim, match)

    def _fuzzy_search(self, keyword: str, row_scores: dict,
                      min_similarity: float):
        """계층 3: rapidfuzz 기반 퍼지 매칭"""
        if not self.index.vocabulary:
            return

        kw_lower = keyword.lower()
        # 임계값을 0~100 스케일로 변환 (rapidfuzz 기준)
        cutoff = min_similarity * 100

        # 어휘 목록에서 유사한 토큰 찾기
        vocab_list = list(self.index.vocabulary)
        matches = rfprocess.extract(
            kw_lower, vocab_list,
            scorer=fuzz.WRatio,
            score_cutoff=cutoff,
            limit=50
        )

        for matched_token, score_100, _ in matches:
            sim = score_100 / 100.0
            # 정확 매칭과 중복되는 결과는 건너뛰기
            if matched_token == kw_lower:
                continue

            cell_indices = self.index.inverted_index.get(matched_token, set())
            for cell_idx in cell_indices:
                cell = self.index.cells[cell_idx]
                if cell is None:
                    continue

                row_key = (cell.file_path, cell.sheet_name, cell.row_idx)
                weighted_score = self.WEIGHT_FUZZY * sim
                match = MatchDetail(
                    col_name=cell.col_name,
                    cell_value=cell.value,
                    match_type='fuzzy',
                    similarity=sim
                )
                self._update_row_score(
                    row_scores, row_key, weighted_score, 'fuzzy', sim, match
                )

    def _range_search(self, min_val: float, max_val: float,
                      row_scores: dict):
        """숫자 범위 검색: min_val 이상 max_val 이하인 숫자가 있는 셀 탐색"""
        for cell_idx, cell in enumerate(self.index.cells):
            if cell is None:
                continue
            try:
                # 쉼표 제거 후 숫자 변환 시도
                num_val = float(cell.value.replace(',', '').strip())
                if min_val <= num_val <= max_val:
                    row_key = (cell.file_path, cell.sheet_name, cell.row_idx)
                    match = MatchDetail(
                        col_name=cell.col_name,
                        cell_value=cell.value,
                        match_type='range',
                        similarity=0.9
                    )
                    self._update_row_score(
                        row_scores, row_key, self.WEIGHT_RANGE, 'range', 0.9, match
                    )
            except (ValueError, AttributeError):
                continue

    def _apply_bm25(self, query: str, row_scores: dict):
        """계층 4: BM25 관련도 점수를 기존 결과에 가산"""
        bm25_scores = self.index.get_bm25_scores(query)
        if not bm25_scores:
            return

        # BM25 점수 정규화 (최대값 기준)
        max_bm25 = max(bm25_scores.values()) if bm25_scores else 1.0
        if max_bm25 == 0:
            return

        for row_key, bm25_score in bm25_scores.items():
            if row_key in row_scores:
                normalized = (bm25_score / max_bm25) * self.WEIGHT_BM25
                row_scores[row_key]['score'] += normalized

    def _apply_excludes(self, excludes: List[str], row_scores: dict):
        """제외 조건: 제외 키워드가 포함된 행을 결과에서 제거"""
        keys_to_remove = []
        for row_key in row_scores:
            row_data = self.index.rows.get(row_key)
            if row_data is None:
                continue
            row_text = ' '.join(row_data.cells.values()).lower()
            for ex in excludes:
                if ex.lower() in row_text:
                    keys_to_remove.append(row_key)
                    break

        for key in keys_to_remove:
            del row_scores[key]

    def _apply_and_condition(self, keywords: List[str], row_scores: dict):
        """AND 조건: 모든 키워드가 행에 포함되어야 결과에 유지"""
        keys_to_remove = []
        for row_key in row_scores:
            row_data = self.index.rows.get(row_key)
            if row_data is None:
                continue
            row_text = ' '.join(row_data.cells.values()).lower()
            all_found = all(kw.lower() in row_text for kw in keywords)
            if not all_found:
                keys_to_remove.append(row_key)

        for key in keys_to_remove:
            del row_scores[key]

    @staticmethod
    def _update_row_score(row_scores: dict, row_key: tuple,
                          score: float, match_type: str,
                          similarity: float, match: MatchDetail):
        """행별 점수를 누적 갱신합니다. 최고 유사도와 매칭 유형을 추적."""
        if row_key not in row_scores:
            row_scores[row_key] = {
                'score': score,
                'match_type': match_type,
                'similarity': similarity,
                'matches': [match]
            }
        else:
            entry = row_scores[row_key]
            entry['score'] = max(entry['score'], score)
            if similarity > entry['similarity']:
                entry['similarity'] = similarity
                entry['match_type'] = match_type
            # 중복 매칭 방지 (같은 셀은 1회만)
            existing = {(m.col_name, m.cell_value) for m in entry['matches']}
            if (match.col_name, match.cell_value) not in existing:
                entry['matches'].append(match)
