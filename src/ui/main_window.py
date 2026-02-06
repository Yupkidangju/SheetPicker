from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QMessageBox, QFileDialog, QMenu
from PySide6.QtCore import Slot, Qt
from PySide6.QtGui import QAction, QIcon
from src.ui.widgets import FileDropZone, SearchGroup, ResultTable, CopyAction, FavoritesPanel
from src.core.workers import SearchWorker
from src.utils.clipboard_manager import ClipboardManager
from src.utils.exporter import ResultExporter
from src.utils.config import ConfigManager
from src.ui.styles import AppStyle
from src.ui.toast import ToastMessage

class MainWindow(QMainWindow):
    """
    [KR] 메인 윈도우 클래스.
    전체 애플리케이션의 레이아웃을 구성하고 주요 위젯을 배치하며,
    Worker 스레드와 UI 위젯 간의 상호작용을 관리합니다.
    """
    def __init__(self):
        super().__init__()

        # [KR] 초기 설정 로드
        self.config = ConfigManager.load_config()

        # [KR] 윈도우 기본 설정
        self.setWindowTitle("Data Scavenger v1.0.0")
        self.resize(1000, 800)

        # [KR] 테마 적용
        is_dark = self.config.get("theme") == "dark"
        AppStyle.apply_theme(self, is_dark)

        # [KR] 중앙 위젯 및 메인 레이아웃 설정
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # [KR] 메뉴바 설정 (테마 전환)
        menubar = self.menuBar()
        view_menu = menubar.addMenu("View")

        action_toggle_theme = QAction("Toggle Dark/Light Mode", self)
        action_toggle_theme.triggered.connect(self.toggle_theme)
        view_menu.addAction(action_toggle_theme)

        # [KR] 상단 상태 바
        self.lbl_status = QLabel("[!] System Status: Ready to Scan")
        self.lbl_status.setStyleSheet("padding: 5px; border-radius: 4px; font-weight: bold;")

        # [KR] 주요 위젯 인스턴스화
        self.favorites_panel = FavoritesPanel()
        self.drop_zone = FileDropZone()
        self.search_group = SearchGroup()
        self.result_table = ResultTable()
        self.copy_action = CopyAction()
        self.toast = ToastMessage(self)

        # [KR] 위젯 배치
        main_layout.addWidget(self.lbl_status)
        main_layout.addWidget(self.favorites_panel)
        main_layout.addWidget(self.drop_zone, stretch=2)
        main_layout.addWidget(self.search_group)
        main_layout.addWidget(self.result_table, stretch=3)
        main_layout.addWidget(self.copy_action)

        # [KR] 시그널 연결
        self.drop_zone.files_dropped.connect(self.on_files_dropped)
        self.search_group.search_requested.connect(self.start_search)
        self.copy_action.copy_requested.connect(self.on_copy_requested)
        self.copy_action.export_requested.connect(self.on_export_requested)
        self.favorites_panel.add_favorite_requested.connect(self.on_favorite_added)

        # [KR] 초기화 (설정값 적용)
        self.favorites_panel.set_favorites(self.config.get("favorites", []))
        hist = self.config.get("search_history", [])
        if hist:
            self.search_group.input_keyword.addItems(hist)

        # [KR] Worker 참조 변수
        self.worker = None

    def toggle_theme(self):
        current_theme = self.config.get("theme", "light")
        new_theme = "dark" if current_theme == "light" else "light"

        ConfigManager.set("theme", new_theme)
        self.config["theme"] = new_theme

        AppStyle.apply_theme(self, new_theme == "dark")
        self.show_toast(f"Switched to {new_theme.capitalize()} Mode")

    def show_toast(self, message):
        self.toast.show_message(message)

    @Slot(str)
    def on_favorite_added(self, path):
        """
        [KR] 즐겨찾기 패널에서 추가 요청 시
        """
        self.drop_zone.list_files.addItem(path)
        self.show_toast(f"Added favorite path: {path}")

    @Slot(str, bool, bool, bool, list)
    def start_search(self, keyword, by_column, case_sensitive, use_regex, target_columns):
        """
        [KR] 검색 시작 처리.
        SearchWorker를 생성하고 시작합니다.
        """
        target_files = self.drop_zone.get_all_files()

        if not target_files:
            self.show_toast("Please drop files to search first.")
            return

        # [KR] 히스토리 저장
        history = [self.search_group.input_keyword.itemText(i) for i in range(self.search_group.input_keyword.count())]
        ConfigManager.set("search_history", history)

        # [KR] 기존 작업 중단 및 UI 초기화
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait()

        self.result_table.clear_results()
        self.result_table.set_keyword(keyword) # 하이라이팅 설정
        self.lbl_status.setText(f"Searching for '{keyword}'...")
        self.search_group.btn_search.setEnabled(False)

        # [KR] Worker 설정 및 시작
        self.worker = SearchWorker(target_files, keyword, by_column, case_sensitive, use_regex)
        self.worker.target_columns = target_columns # 속성 주입

        self.worker.result_found.connect(self.on_result_found)
        self.worker.progress_updated.connect(self.update_status)
        self.worker.error_occurred.connect(self.on_worker_error)
        self.worker.finished_task.connect(self.on_search_finished)
        self.worker.start()

    @Slot(list)
    def on_files_dropped(self, files):
        self.lbl_status.setText(f"Added {len(files)} files/folders to scan list.")

    @Slot(list)
    def on_result_found(self, results):
        """
        [KR] 검색 결과 수신 시 테이블에 추가 (Batch 처리)
        """
        self.result_table.add_result_rows(results)

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

    @Slot()
    def on_copy_requested(self):
        """
        [KR] 선택된 항목을 클립보드로 복사합니다.
        """
        selected_rows = []
        table = self.result_table.table_results

        for row in range(table.rowCount()):
            # 체크박스 확인 (0번 컬럼)
            chk_item = table.item(row, 0)
            if chk_item.checkState() == Qt.CheckState.Checked:
                data = {
                    'file': table.item(row, 1).text(),
                    'sheet': table.item(row, 2).text(),
                    'data': table.item(row, 3).text()
                }
                selected_rows.append(data)

        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select items to copy.")
            return

        formatted_text = ClipboardManager.format_for_clipboard(selected_rows)

        # [KR] 개인정보 경고 (Spec)
        reply = QMessageBox.question(
            self,
            "Privacy Warning",
            "Selected data may contain sensitive information.\nProceed to copy to system clipboard?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            if ClipboardManager.copy_to_clipboard(formatted_text):
                self.lbl_status.setText(f"Copied {len(selected_rows)} items to clipboard.")
            else:
                QMessageBox.critical(self, "Error", "Failed to access clipboard.")

    @Slot()
    def on_export_requested(self):
        """
        [KR] 검색 결과를 엑셀/CSV로 내보냅니다.
        체크된 항목이 있으면 체크된 항목만, 없으면 전체 항목을 내보냅니다.
        """
        table = self.result_table.table_results
        if table.rowCount() == 0:
            QMessageBox.warning(self, "No Data", "There is no data to export.")
            return

        # 1. 대상 데이터 수집
        target_data = []
        has_checked = False

        # 체크된 항목 먼저 확인
        for row in range(table.rowCount()):
            if table.item(row, 0).checkState() == Qt.CheckState.Checked:
                has_checked = True
                break

        for row in range(table.rowCount()):
            item = table.item(row, 0)
            # 체크된 것이 있으면 체크된 것만, 없으면 전체
            if has_checked and item.checkState() != Qt.CheckState.Checked:
                continue

            data_map = item.data(Qt.ItemDataRole.UserRole)
            if data_map and 'raw_data' in data_map:
                # 메타데이터 추가 (파일명, 시트명)
                row_data = data_map['raw_data'].copy()
                row_data['_File'] = table.item(row, 1).text()
                row_data['_Sheet'] = table.item(row, 2).text()
                target_data.append(row_data)

        if not target_data:
             QMessageBox.warning(self, "No Data", "Failed to collect data for export.")
             return

        # 2. 저장 경로 선택
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Results",
            "search_results.xlsx",
            "Excel Files (*.xlsx);;CSV Files (*.csv)"
        )

        if not file_path:
            return

        # 3. 내보내기 실행
        try:
            ResultExporter.export(target_data, file_path)
            self.lbl_status.setText(f"Exported {len(target_data)} items to {file_path}")
            QMessageBox.information(self, "Export Success", f"Successfully exported {len(target_data)} items.")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", str(e))

    def closeEvent(self, event):
        # [KR] 앱 종료 시 스레드 안전 종료
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait()
        super().closeEvent(event)
