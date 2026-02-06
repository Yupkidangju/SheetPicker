import pandas as pd
from typing import Optional, List, Any

class DataSearcher:
    """
    [KR] 데이터 검색 엔진 클래스.
    Pandas DataFrame을 기반으로 행(Row) 또는 열(Column) 단위의 고속 검색을 수행합니다.
    """

    @staticmethod
    def search_dataframe(
        df: pd.DataFrame,
        keyword: str,
        by_column: bool = False,
        case_sensitive: bool = False,
        use_regex: bool = False,
        target_columns: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        [KR] DataFrame 내에서 키워드를 검색하고, 매칭되는 행(Row)들을 반환합니다.

        Args:
            df (pd.DataFrame): 검색 대상 데이터프레임
            keyword (str): 검색할 문자열 (또는 정규식 패턴)
            by_column (bool): True일 경우 데이터를 전치(Transpose)하여 '열'을 '행'처럼 검색합니다.
            case_sensitive (bool): 대소문자 구분 여부
            use_regex (bool): True일 경우 keyword를 정규식으로 처리합니다.
            target_columns (List[str]): 검색할 컬럼명 리스트. None이면 전체 컬럼 검색.

        Returns:
            pd.DataFrame: 검색 조건에 매칭된 행만 포함하는 데이터프레임
        """
        if df.empty or not keyword:
            return pd.DataFrame() # 빈 결과 반환

        # [KR] 검색 대상 데이터 준비
        # by_column이 True이면 전치하여 Column을 Row로 변환 (Spec: 결과는 항상 Row 형태)
        target_df = df.T if by_column else df

        # [KR] 모든 데이터를 문자열로 변환하여 검색
        # NaN 값은 빈 문자열로 처리하여 에러 방지
        # applymap/map은 느리므로 stack() 또는 astype(str) 사용 권장
        # 여기서는 전체를 문자열로 변환 후 contains 적용

        # 1. 효율성을 위해 전체를 String으로 변환
        str_df = target_df.astype(str)

        # [KR] 컬럼 타겟팅 적용
        search_scope_df = str_df
        if target_columns:
             # 존재하는 컬럼만 필터링
             valid_cols = [c for c in target_columns if c in str_df.columns]
             if valid_cols:
                 search_scope_df = str_df[valid_cols]

        # 2. 행(Axis 1) 단위로 하나라도 키워드를 포함하는지 검사
        # [KR] 메모리 최적화: apply() 대신 컬럼 순회 루프 사용

        # [KR] v1.2.0 Smart Search Logic
        # 정규식이 아니고, 키워드에 공백/파이프/마이너스가 있으면 스마트 검색 시도
        is_smart = not use_regex and any(c in keyword for c in [' ', '|', '-'])

        if is_smart:
            return DataSearcher._smart_search(target_df, search_scope_df, keyword, case_sensitive)

        # 기존 로직 (Literal or Regex)
        try:
            mask = DataSearcher._get_mask(search_scope_df, keyword, case_sensitive, use_regex)
            if mask is None:
                return pd.DataFrame()
            return target_df[mask]
        except Exception:
            return pd.DataFrame()

    @staticmethod
    def _get_mask(df, keyword, case, regex):
        """
        [KR] 단일 키워드에 대한 boolean 마스크를 생성합니다 (컬럼 순회 방식).
        """
        mask = None
        for col in df.columns:
            col_mask = df[col].str.contains(keyword, case=case, regex=regex, na=False)
            if mask is None:
                mask = col_mask
            else:
                mask |= col_mask
        return mask

    @staticmethod
    def _smart_search(target_df, scope_df, query, case_sensitive):
        """
        [KR] 스마트 검색 로직.
        AND(공백), OR(|), NOT(-) 조건을 순차적으로 적용합니다.
        """
        import shlex

        try:
            # 1. 쿼리 파싱 (따옴표 처리)
            # shlex는 쉘 스타일 파싱을 제공하므로 "hello world"를 하나의 토큰으로 인식함.
            tokens = shlex.split(query)
        except:
            # 파싱 실패 시 기본 공백 분리
            tokens = query.split()

        # [KR] 필터링 시작: 전체가 True인 마스크로 시작하지 않고,
        # Pandas chaining을 위해 DataFrame을 단계적으로 줄여나가는 것이 빠름.
        # 하지만 원본 인덱스를 유지해야 하므로 Boolean Indexing을 조합함.

        # 초기 마스크: 전체 True
        final_mask = pd.Series([True] * len(scope_df), index=scope_df.index)

        for token in tokens:
            if not token: continue

            # OR 조건 처리 (A|B)
            if '|' in token:
                sub_tokens = token.split('|')
                or_mask = None
                for sub in sub_tokens:
                    if not sub: continue
                    m = DataSearcher._get_mask(scope_df, sub, case_sensitive, False)
                    if m is not None:
                        or_mask = m if or_mask is None else (or_mask | m)

                if or_mask is not None:
                    final_mask &= or_mask

            # NOT 조건 처리 (-A)
            elif token.startswith('-') and len(token) > 1:
                keyword = token[1:]
                m = DataSearcher._get_mask(scope_df, keyword, case_sensitive, False)
                if m is not None:
                    final_mask &= ~m # NOT

            # AND 조건 처리 (A)
            else:
                m = DataSearcher._get_mask(scope_df, token, case_sensitive, False)
                if m is not None:
                    final_mask &= m

        return target_df[final_mask]

    @staticmethod
    def format_result_row(row: pd.Series) -> str:
        """
        [KR] 검색 결과(행)를 UI 표시용 미리보기 문자열로 변환합니다.
        """
        # 앞 5개 컬럼만, 각 값은 20자로 제한하여 결합
        return " | ".join([str(val)[:20] for val in row.values[:5]])
