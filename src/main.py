import sys
from PySide6.QtWidgets import QApplication
from src.ui.main_window import MainWindow
from src.utils.logger import logger

# [KR] 애플리케이션 진입점
def main():
    """
    [KR] 메인 애플리케이션 실행 함수.
    QApplication을 초기화하고 메인 윈도우를 표시합니다.
    """
    logger.info("Starting Data Scavenger Application...")

    app = QApplication(sys.argv)

    # [KR] 메인 윈도우 생성 및 표시
    try:
        window = MainWindow()
        window.show()
        logger.info("Main window displayed.")

        exit_code = app.exec()
        logger.info(f"Application exiting with code {exit_code}.")
        sys.exit(exit_code)

    except Exception as e:
        logger.critical(f"Unhandled exception in main loop: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
