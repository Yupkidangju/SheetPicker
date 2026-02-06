import pandas as pd
import re2
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
        try:
            if use_regex:
                # [KR] 보안: ReDoS 방지를 위해 google-re2 사용
                # 정규식 모드일 때는 pandas의 str.contains(regex=True) 대신 re2를 직접 적용
                pattern_str = keyword
                if not case_sensitive:
                    pattern_str = "(?i)" + pattern_str

                # re2 컴파일 (실패 시 예외 발생으로 catch 블록 이동)
                pattern = re2.compile(pattern_str)

                # [KR] 요소별로 re2 검색 수행 (pandas >= 2.1.0 DataFrame.map 사용)
                # google-re2는 C++ 기반이라 매우 빠르지만, Python Loop 오버헤드는 존재함
                # 그러나 ReDoS 방지를 위해 필수적임
                mask = search_scope_df.map(
                    lambda x: bool(pattern.search(x))
                ).any(axis=1)
            else:
                # [KR] 리터럴 검색은 pandas 최적화 기능 사용 (속도 빠름)
                # use_regex가 False이면 regex=False가 되어 literal 매칭.
                mask = search_scope_df.apply(
                    lambda x: x.str.contains(keyword, case=case_sensitive, regex=False, na=False)
                ).any(axis=1)
        except Exception:
            # [KR] 정규식 오류 등이 발생하면 빈 결과를 반환하여 크래시 방지
            return pd.DataFrame()

        # [KR] 필터링된 결과 반환 (원본 DataFrame에서 행 선택)
        return target_df[mask]

    @staticmethod
    def format_result_row(row: Any) -> str:
        """
        [KR] 검색 결과(행)를 UI 표시용 미리보기 문자열로 변환합니다.
        """
        # 앞 5개 컬럼만, 각 값은 20자로 제한하여 결합
        values = row.values if hasattr(row, 'values') else row
        return " | ".join([str(val)[:20] for val in values[:5]])
