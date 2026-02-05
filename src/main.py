import sys
from PySide6.QtWidgets import QApplication
from src.ui.main_window import MainWindow

# [KR] 애플리케이션 진입점
def main():
    """
    [KR] 메인 애플리케이션 실행 함수.
    QApplication을 초기화하고 메인 윈도우를 표시합니다.
    """
    app = QApplication(sys.argv)

    # [KR] 메인 윈도우 생성 및 표시
    window = MainWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
