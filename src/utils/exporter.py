"""
[v2.0.0] 검색 결과 내보내기 유틸리티
검색 결과를 Excel(.xlsx) 또는 CSV(.csv) 파일로 내보냅니다.
체크된 결과만 또는 전체 결과를 내보낼 수 있습니다.
"""

import pandas as pd
from pathlib import Path
from typing import List
from src.utils.logger import logger


class ResultExporter:
    """
    [v2.0.0] 검색 결과 내보내기.
    SearchResult 리스트를 받아 Excel/CSV로 저장합니다.
    출처 파일/시트 정보를 포함하여 추적성을 보장합니다.
    """

    @staticmethod
    def export_results(results, file_path: str):
        """
        검색 결과를 파일로 내보냅니다.

        Args:
            results: List[SearchResult] — 내보낼 검색 결과
            file_path: 저장할 파일 경로 (.xlsx 또는 .csv)
        """
        if not results:
            logger.warning("내보낼 결과가 없습니다")
            return

        # 결과를 DataFrame으로 변환
        rows = []
        for r in results:
            row_dict = {
                '_출처파일': r.row.file_name,
                '_시트': r.row.sheet_name,
                '_매칭유형': r.match_type,
                '_유사도': f"{r.similarity:.0%}",
            }
            # 원본 데이터 셀 추가
            for header in r.row.headers:
                row_dict[header] = r.row.cells.get(header, '')
            rows.append(row_dict)

        df = pd.DataFrame(rows)

        # 파일 형식에 따라 저장
        ext = Path(file_path).suffix.lower()
        try:
            if ext == '.csv':
                df.to_csv(file_path, index=False, encoding='utf-8-sig')
            else:
                df.to_excel(file_path, index=False, engine='openpyxl')

            logger.info(f"내보내기 완료: {file_path} ({len(rows)}건)")
        except Exception as e:
            logger.error(f"내보내기 실패: {e}", exc_info=True)
            raise

    @staticmethod
    def export_dataframe(df: pd.DataFrame, file_path: str):
        """
        DataFrame을 파일로 직접 내보냅니다 (범용).

        Args:
            df: pandas DataFrame
            file_path: 저장할 파일 경로
        """
        ext = Path(file_path).suffix.lower()
        try:
            if ext == '.csv':
                df.to_csv(file_path, index=False, encoding='utf-8-sig')
            else:
                df.to_excel(file_path, index=False, engine='openpyxl')
        except Exception as e:
            logger.error(f"DataFrame 내보내기 실패: {e}", exc_info=True)
            raise
