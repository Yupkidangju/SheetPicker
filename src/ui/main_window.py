from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QMessageBox
from PySide6.QtCore import Slot
from src.ui.widgets import FileDropZone, SearchGroup, ResultTable, CopyAction
from src.core.workers import SearchWorker

class MainWindow(QMainWindow):
    """
    [KR] 메인 윈도우 클래스.
    전체 애플리케이션의 레이아웃을 구성하고 주요 위젯을 배치하며,
    Worker 스레드와 UI 위젯 간의 상호작용을 관리합니다.
    """
    def __init__(self):
        super().__init__()

        # [KR] 윈도우 기본 설정
        self.setWindowTitle("Data Scavenger v0.1 BETA")
        self.resize(900, 700)

        # [KR] 중앙 위젯 및 메인 레이아웃 설정
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # [KR] 상단 상태 바
        self.lbl_status = QLabel("[!] System Status: Ready to Scan")
        self.lbl_status.setStyleSheet("background-color: #f0f0f0; padding: 5px; border-radius: 4px;")

        # [KR] 주요 위젯 인스턴스화
        self.drop_zone = FileDropZone()
        self.search_group = SearchGroup()
        self.result_table = ResultTable()
        self.copy_action = CopyAction()

        # [KR] 위젯 배치
        main_layout.addWidget(self.lbl_status)
        main_layout.addWidget(self.drop_zone, stretch=2)
        main_layout.addWidget(self.search_group)
        main_layout.addWidget(self.result_table, stretch=3)
        main_layout.addWidget(self.copy_action)

        # [KR] 시그널 연결
        self.drop_zone.files_dropped.connect(self.on_files_dropped)
        self.search_group.search_requested.connect(self.start_search)

        # [KR] Worker 참조 변수
        self.worker = None

    @Slot(list)
    def on_files_dropped(self, files):
        self.lbl_status.setText(f"Added {len(files)} files/folders to scan list.")

    @Slot(str, bool, bool)
    def start_search(self, keyword, by_column, case_sensitive):
        """
        [KR] 검색 시작 처리.
        SearchWorker를 생성하고 시작합니다.
        """
        target_files = self.drop_zone.get_all_files()

        if not target_files:
            QMessageBox.warning(self, "No Files", "Please drop files to search first.")
            return

        # [KR] 기존 작업 중단 및 UI 초기화
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait()

        self.result_table.clear_results()
        self.lbl_status.setText(f"Searching for '{keyword}'...")
        self.search_group.btn_search.setEnabled(False) # 중복 실행 방지

        # [KR] Worker 설정 및 시작
        self.worker = SearchWorker(target_files, keyword, by_column, case_sensitive)
        self.worker.result_found.connect(self.on_result_found)
        self.worker.progress_updated.connect(self.update_status)
        self.worker.error_occurred.connect(self.on_worker_error)
        self.worker.finished_task.connect(self.on_search_finished)
        self.worker.start()

    @Slot(dict)
    def on_result_found(self, result):
        """
        [KR] 검색 결과 수신 시 테이블에 추가
        """
        self.result_table.add_result_row(
            result['file'],
            result['sheet'],
            result['preview']
        )

    @Slot(str)
    def update_status(self, msg):
        self.lbl_status.setText(f"[Busy] {msg}")

    @Slot(str)
    def on_worker_error(self, err_msg):
        # [KR] 에러 발생 시 상태창에 표시 (팝업은 너무 잦을 수 있으므로 지양)
        self.lbl_status.setText(f"[Error] {err_msg}")
        # 필요 시 로그 위젯 등에 추가 가능

    @Slot()
    def on_search_finished(self):
        self.lbl_status.setText("[Done] Search completed.")
        self.search_group.btn_search.setEnabled(True)

        if self.result_table.table_results.rowCount() == 0:
            QMessageBox.information(self, "Search Result", "No matches found.")

    def closeEvent(self, event):
        # [KR] 앱 종료 시 스레드 안전 종료
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait()
        super().closeEvent(event)
