from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QListWidget,
    QTableWidget, QGroupBox, QHBoxLayout, QRadioButton,
    QLineEdit, QCheckBox
)
from PySide6.QtCore import Qt

class FileDropZone(QWidget):
    """
    [KR] 파일 드롭 영역 위젯.
    사용자가 파일이나 폴더를 드래그 앤 드롭하는 영역입니다.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        self.setLayout(layout)

        # [KR] UI 구성: 안내 레이블 및 파일 리스트
        self.lbl_info = QLabel("[ Drop Files/Folders Here ]")
        self.lbl_info.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.list_files = QListWidget()

        layout.addWidget(self.lbl_info)
        layout.addWidget(self.list_files)

class SearchGroup(QWidget):
    """
    [KR] 검색 옵션 및 입력 위젯 그룹.
    행/열 선택, 대소문자 구분, 검색어 입력 기능을 제공합니다.
    """
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
        self.btn_search = QPushButton("[ SEARCH ]")

        input_layout.addWidget(self.input_keyword)
        input_layout.addWidget(self.btn_search)

        layout.addWidget(self.grp_options)
        layout.addLayout(input_layout)

class ResultTable(QWidget):
    """
    [KR] 검색 결과 표시 위젯.
    검색된 데이터를 테이블 형태로 보여주고 체크박스 선택을 지원합니다.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.lbl_title = QLabel("Results Index:")
        self.table_results = QTableWidget()
        self.table_results.setColumnCount(4)
        self.table_results.setHorizontalHeaderLabels(["[X]", "Source", "Sheet", "Preview (Row Data)"])

        layout.addWidget(self.lbl_title)
        layout.addWidget(self.table_results)

class CopyAction(QWidget):
    """
    [KR] 하단 액션 바 위젯.
    선택된 항목 개수를 표시하고 클립보드 복사 기능을 제공합니다.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout()
        self.setLayout(layout)

        self.lbl_selected = QLabel("[ Selected: 0 items ]")
        self.btn_copy = QPushButton("[ COPY TO CLIPBOARD ]")

        layout.addWidget(self.lbl_selected)
        layout.addStretch()
        layout.addWidget(self.btn_copy)
