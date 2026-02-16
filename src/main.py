"""
[v2.0.0] Data Scavenger 진입점
앱을 초기화하고 메인 윈도우를 표시합니다.
"""

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont
from src.ui.main_window import MainWindow
from src.utils.logger import logger


def main():
    """앱 실행"""
    logger.info("Data Scavenger v2.0.0 시작")

    app = QApplication(sys.argv)

    # 기본 폰트 설정 (한국어 최적화)
    font = QFont()
    font.setFamilies(["Pretendard", "Malgun Gothic", "Segoe UI"])
    font.setPointSize(10)
    app.setFont(font)

    # 메인 윈도우 생성 및 표시
    window = MainWindow()
    window.show()

    exit_code = app.exec()
    logger.info(f"앱 종료 (코드: {exit_code})")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
