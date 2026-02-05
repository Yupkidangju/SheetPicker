import pandas as pd
from typing import List, Dict

class ResultExporter:
    """
    [KR] 검색 결과를 파일로 내보내는 유틸리티 클래스.
    """

    @staticmethod
    def export(data: List[Dict], file_path: str):
        """
        [KR] 데이터 리스트를 지정된 파일 경로로 저장합니다.
        확장자에 따라 Excel 또는 CSV로 저장합니다.

        Args:
            data (List[Dict]): 저장할 데이터 리스트 (각 항목은 딕셔너리)
            file_path (str): 저장할 파일 경로 (.xlsx, .csv)
        """
        if not data:
            return

        # [KR] DataFrame 변환
        df = pd.DataFrame(data)

        if file_path.endswith('.xlsx'):
            df.to_excel(file_path, index=False)
        elif file_path.endswith('.csv'):
            df.to_csv(file_path, index=False, encoding='utf-8-sig')
        else:
            raise ValueError("Unsupported file format. Please use .xlsx or .csv")
