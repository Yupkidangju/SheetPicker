import pyperclip
from typing import List, Dict

class ClipboardManager:
    """
    [KR] 클립보드 관리 클래스.
    데이터를 엑셀과 호환되는 TSV(Tab-Separated Values) 포맷으로 변환하고 시스템 클립보드로 복사합니다.
    """

    @staticmethod
    def format_for_clipboard(rows: List[Dict[str, str]]) -> str:
        """
        [KR] 검색 결과 리스트를 클립보드용 문자열로 변환합니다.

        Args:
            rows (List[Dict]): {'file': str, 'sheet': str, 'data': str} 형태의 딕셔너리 리스트

        Returns:
            str: 탭(\t)으로 구분된 문자열
        """
        if not rows:
            return ""

        # [KR] 헤더 생성
        lines = ["Source File\tSheet Name\tRow Data"]

        # [KR] 데이터 행 변환
        for row in rows:
            # 줄바꿈 문자 제거 (한 줄로 유지하기 위함)
            clean_data = row.get('data', '').replace('\n', ' ').replace('\r', '')
            line = f"{row.get('file', '')}\t{row.get('sheet', '')}\t{clean_data}"
            lines.append(line)

        return "\n".join(lines)

    @staticmethod
    def copy_to_clipboard(text: str) -> bool:
        """
        [KR] 텍스트를 시스템 클립보드에 복사합니다.

        Args:
            text (str): 복사할 텍스트

        Returns:
            bool: 성공 여부
        """
        try:
            pyperclip.copy(text)
            return True
        except Exception as e:
            # [KR] 복사 실패 시 (로그만 남기고 False 반환)
            print(f"Clipboard copy failed: {e}")
            return False
