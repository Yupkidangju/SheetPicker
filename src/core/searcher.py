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
        case_sensitive: bool = False
    ) -> pd.DataFrame:
        """
        [KR] DataFrame 내에서 키워드를 검색하고, 매칭되는 행(Row)들을 반환합니다.

        Args:
            df (pd.DataFrame): 검색 대상 데이터프레임
            keyword (str): 검색할 문자열
            by_column (bool): True일 경우 데이터를 전치(Transpose)하여 '열'을 '행'처럼 검색합니다.
            case_sensitive (bool): 대소문자 구분 여부

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

        # 2. 행(Axis 1) 단위로 하나라도 키워드를 포함하는지 검사
        # case_sensitive 옵션 적용
        mask = str_df.apply(
            lambda x: x.str.contains(keyword, case=case_sensitive, na=False)
        ).any(axis=1)

        # [KR] 필터링된 결과 반환
        return target_df[mask]

    @staticmethod
    def format_result_row(row: pd.Series) -> str:
        """
        [KR] 검색 결과(행)를 UI 표시용 미리보기 문자열로 변환합니다.
        """
        # 앞 5개 컬럼만, 각 값은 20자로 제한하여 결합
        return " | ".join([str(val)[:20] for val in row.values[:5]])
