from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel
from src.ui.widgets import FileDropZone, SearchGroup, ResultTable, CopyAction

class MainWindow(QMainWindow):
    """
    [KR] 메인 윈도우 클래스.
    전체 애플리케이션의 레이아웃을 구성하고 주요 위젯을 배치합니다.
    """
    def __init__(self):
        super().__init__()

        # [KR] 윈도우 기본 설정
        self.setWindowTitle("Data Scavenger v0.1 BETA")
        self.resize(800, 600)

        # [KR] 중앙 위젯 및 메인 레이아웃 설정
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # [KR] 상단 상태 바 (임시 구현)
        self.lbl_status = QLabel("[!] System Status: Ready to Scan")
        self.lbl_status.setStyleSheet("background-color: #f0f0f0; padding: 5px;")

        # [KR] 주요 위젯 인스턴스화 및 배치
        self.drop_zone = FileDropZone()
        self.search_group = SearchGroup()
        self.result_table = ResultTable()
        self.copy_action = CopyAction()

        main_layout.addWidget(self.lbl_status)
        main_layout.addWidget(self.drop_zone)
        main_layout.addWidget(self.search_group)
        main_layout.addWidget(self.result_table)
        main_layout.addWidget(self.copy_action)
