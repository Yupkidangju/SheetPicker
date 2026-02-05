from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QListWidget,
    QTableWidget, QGroupBox, QHBoxLayout, QRadioButton,
    QLineEdit, QCheckBox, QAbstractItemView, QTableWidgetItem
)
from PySide6.QtCore import Qt, Signal
from src.core.scanner import FileScanner

class FileDropZone(QWidget):
    """
    [KR] 파일 드롭 영역 위젯.
    사용자가 파일이나 폴더를 드래그 앤 드롭하는 영역입니다.
    """
    files_dropped = Signal(list) # [KR] 파일 드롭 시 메인 윈도우로 경로 리스트 전달

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.setAcceptDrops(True) # [KR] 드래그 앤 드롭 활성화
        self.scanner = FileScanner()

        # [KR] UI 구성: 안내 레이블 및 파일 리스트
        self.lbl_info = QLabel("[ Drop Files/Folders Here ]")
        self.lbl_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_info.setStyleSheet("border: 2px dashed #aaa; padding: 10px; color: #555;")

        self.list_files = QListWidget()
        self.list_files.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)

        # [KR] 파일 삭제 버튼
        btn_layout = QHBoxLayout()
        self.btn_clear = QPushButton("Clear All")
        self.btn_remove = QPushButton("Remove Selected")

        self.btn_clear.clicked.connect(self.list_files.clear)
        self.btn_remove.clicked.connect(self.remove_selected_items)

        btn_layout.addWidget(self.btn_remove)
        btn_layout.addWidget(self.btn_clear)

        layout.addWidget(self.lbl_info)
        layout.addWidget(self.list_files)
        layout.addLayout(btn_layout)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        files = [u.toLocalFile() for u in event.mimeData().urls()]

        # [KR] 지원되는 파일만 필터링 (Scanner 사용)
        supported_files = self.scanner.get_supported_files(files)

        if supported_files:
            self.list_files.addItems(supported_files)
            self.files_dropped.emit(supported_files)

        event.accept()

    def remove_selected_items(self):
        for item in self.list_files.selectedItems():
            self.list_files.takeItem(self.list_files.row(item))

    def get_all_files(self):
        return [self.list_files.item(i).text() for i in range(self.list_files.count())]

class SearchGroup(QWidget):
    """
    [KR] 검색 옵션 및 입력 위젯 그룹.
    행/열 선택, 대소문자 구분, 검색어 입력 기능을 제공합니다.
    """
    search_requested = Signal(str, bool, bool) # keyword, by_column, case_sensitive

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        self.setLayout(layout)

        # [KR] 검색 옵션 그룹
        self.grp_options = QGroupBox("Search Strategy")
        opt_layout = QHBoxLayout()
        self.grp_options.setLayout(opt_layout)

        self.radio_row = QRadioButton("Search by Row")
        self.radio_col = QRadioButton("Search by Column")
        self.radio_col.setChecked(True) # [KR] 기본값: 열 검색
        self.chk_case = QCheckBox("Case Sensitive")
        self.chk_case.setChecked(True) # [KR] 기본값: 대소문자 구분

        opt_layout.addWidget(self.radio_row)
        opt_layout.addWidget(self.radio_col)
        opt_layout.addWidget(self.chk_case)

        # [KR] 검색어 입력 및 버튼
        input_layout = QHBoxLayout()
        self.input_keyword = QLineEdit()
        self.input_keyword.setPlaceholderText("Enter search keyword...")
        self.input_keyword.returnPressed.connect(self.emit_search) # 엔터 키 지원

        self.btn_search = QPushButton("[ SEARCH ]")
        self.btn_search.clicked.connect(self.emit_search)

        input_layout.addWidget(self.input_keyword)
        input_layout.addWidget(self.btn_search)

        layout.addWidget(self.grp_options)
        layout.addLayout(input_layout)

    def emit_search(self):
        keyword = self.input_keyword.text().strip()
        if not keyword:
            return

        by_column = self.radio_col.isChecked()
        case_sensitive = self.chk_case.isChecked()
        self.search_requested.emit(keyword, by_column, case_sensitive)

class ResultTable(QWidget):
    """
    [KR] 검색 결과 표시 위젯.
    검색된 데이터를 테이블 형태로 보여주고 체크박스 선택을 지원합니다.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.lbl_title = QLabel("Results Index: 0 found")
        self.table_results = QTableWidget()
        self.table_results.setColumnCount(4)
        self.table_results.setHorizontalHeaderLabels(["[X]", "Source", "Sheet", "Preview (Row Data)"])
        self.table_results.setColumnWidth(0, 30) # 체크박스 컬럼 너비
        self.table_results.setColumnWidth(1, 150)
        self.table_results.setColumnWidth(2, 100)
        self.table_results.horizontalHeader().setStretchLastSection(True)

        layout.addWidget(self.lbl_title)
        layout.addWidget(self.table_results)

    def add_result_row(self, file_name, sheet_name, preview_text):
        row_idx = self.table_results.rowCount()
        self.table_results.insertRow(row_idx)

        # [X] Checkbox Item
        chk_item = QTableWidgetItem()
        chk_item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
        chk_item.setCheckState(Qt.CheckState.Unchecked)
        self.table_results.setItem(row_idx, 0, chk_item)

        self.table_results.setItem(row_idx, 1, QTableWidgetItem(file_name))
        self.table_results.setItem(row_idx, 2, QTableWidgetItem(sheet_name))
        self.table_results.setItem(row_idx, 3, QTableWidgetItem(preview_text))

        self.lbl_title.setText(f"Results Index: {self.table_results.rowCount()} found")

    def clear_results(self):
        self.table_results.setRowCount(0)
        self.lbl_title.setText("Results Index: 0 found")

class CopyAction(QWidget):
    """
    [KR] 하단 액션 바 위젯.
    선택된 항목 개수를 표시하고 클립보드 복사 기능을 제공합니다.
    """
    copy_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout()
        self.setLayout(layout)

        self.lbl_selected = QLabel("[ Selected: 0 items ]")
        self.btn_copy = QPushButton("[ COPY TO CLIPBOARD ]")
        self.btn_copy.clicked.connect(self.copy_requested.emit)
        self.btn_copy.setEnabled(False) # [KR] Phase 5 구현 전까지 비활성화
        self.btn_copy.setToolTip("Coming in v0.2")

        layout.addWidget(self.lbl_selected)
        layout.addStretch()
        layout.addWidget(self.btn_copy)
