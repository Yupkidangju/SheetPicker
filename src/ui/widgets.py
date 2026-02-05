from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QListWidget,
    QTableWidget, QGroupBox, QHBoxLayout, QRadioButton,
    QLineEdit, QCheckBox, QAbstractItemView, QTableWidgetItem,
    QComboBox, QDialog, QHeaderView, QMenu, QToolButton,
    QFormLayout, QStyledItemDelegate
)
from PySide6.QtCore import Qt, Signal, QUrl, QSortFilterProxyModel, QRegularExpression
from PySide6.QtGui import QDesktopServices, QAction, QTextDocument, QAbstractTextDocumentLayout, QPalette
from src.core.scanner import FileScanner

class FavoritesPanel(QWidget):
    """
    [KR] 즐겨찾기 폴더 관리 패널.
    자주 사용하는 경로를 저장하고 원클릭으로 추가합니다.
    """
    add_favorite_requested = Signal(str) # 경로 추가 요청 시그널

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.combo_favorites = QComboBox()
        self.combo_favorites.setPlaceholderText("Select Favorite Folder...")
        self.combo_favorites.setMinimumWidth(200)

        self.btn_add_to_list = QPushButton("Add to Scan List")
        self.btn_add_to_list.setToolTip("Add selected favorite to scan list")
        self.btn_add_to_list.clicked.connect(self.on_add_clicked)

        layout.addWidget(QLabel("Favorites:"))
        layout.addWidget(self.combo_favorites)
        layout.addWidget(self.btn_add_to_list)
        layout.addStretch()

    def set_favorites(self, favorites: list):
        self.combo_favorites.clear()
        self.combo_favorites.addItems(favorites)

    def on_add_clicked(self):
        path = self.combo_favorites.currentText()
        if path:
            self.add_favorite_requested.emit(path)

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
    # keyword, by_column, case_sensitive, use_regex, target_columns
    search_requested = Signal(str, bool, bool, bool, list)

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
        self.chk_regex = QCheckBox("Regex") # [KR] 정규식 옵션 추가

        opt_layout.addWidget(self.radio_row)
        opt_layout.addWidget(self.radio_col)
        opt_layout.addWidget(self.chk_case)
        opt_layout.addWidget(self.chk_regex)

        # [KR] 컬럼 타겟팅 입력
        target_layout = QHBoxLayout()
        target_layout.addWidget(QLabel("Target Columns (Optional):"))
        self.input_target = QLineEdit()
        self.input_target.setPlaceholderText("e.g. Email, Phone, ID (comma separated)")
        target_layout.addWidget(self.input_target)

        # [KR] 검색어 입력 (History ComboBox) 및 버튼
        input_layout = QHBoxLayout()
        self.input_keyword = QComboBox()
        self.input_keyword.setEditable(True)
        self.input_keyword.setPlaceholderText("Enter search keyword...")
        self.input_keyword.lineEdit().returnPressed.connect(self.emit_search) # 엔터 키 지원

        self.btn_search = QPushButton("[ SEARCH ]")
        self.btn_search.clicked.connect(self.emit_search)

        input_layout.addWidget(self.input_keyword, stretch=3)
        input_layout.addWidget(self.btn_search)

        layout.addWidget(self.grp_options)
        layout.addLayout(target_layout)
        layout.addLayout(input_layout)

    def emit_search(self):
        keyword = self.input_keyword.currentText().strip()
        if not keyword:
            return

        # [KR] 히스토리 추가
        self.add_to_history(keyword)

        by_column = self.radio_col.isChecked()
        case_sensitive = self.chk_case.isChecked()
        use_regex = self.chk_regex.isChecked()

        # [KR] 타겟 컬럼 파싱
        target_cols_str = self.input_target.text().strip()
        target_columns = [c.strip() for c in target_cols_str.split(',')] if target_cols_str else None

        self.search_requested.emit(keyword, by_column, case_sensitive, use_regex, target_columns)

    def add_to_history(self, keyword):
        """
        [KR] 검색어를 히스토리에 추가합니다 (중복 제거, 최근 10개 유지)
        """
        # 현재 항목들 가져오기
        items = [self.input_keyword.itemText(i) for i in range(self.input_keyword.count())]

        # 이미 존재하면 제거 (맨 위로 올리기 위함)
        if keyword in items:
            self.input_keyword.removeItem(items.index(keyword))

        # 맨 앞에 추가
        self.input_keyword.insertItem(0, keyword)
        self.input_keyword.setCurrentIndex(0)

        # 10개 초과 시 마지막 제거
        if self.input_keyword.count() > 10:
            self.input_keyword.removeItem(10)

class DetailDialog(QDialog):
    """
    [KR] 상세 보기 팝업 다이얼로그.
    선택된 행의 모든 데이터를 Grid 형태로 보여줍니다.
    """
    def __init__(self, data: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Detail View")
        self.resize(600, 400)

        layout = QVBoxLayout()
        self.setLayout(layout)

        # 정보 표시
        info_label = QLabel("Full Row Data:")
        layout.addWidget(info_label)

        # 테이블 구성
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Column", "Value"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # 데이터 채우기
        self.table.setRowCount(len(data))
        for i, (key, value) in enumerate(data.items()):
            self.table.setItem(i, 0, QTableWidgetItem(str(key)))
            self.table.setItem(i, 1, QTableWidgetItem(str(value)))

        layout.addWidget(self.table)

        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.close)
        layout.addWidget(btn_close)

class HTMLDelegate(QStyledItemDelegate):
    """
    [KR] HTML 태그를 렌더링하기 위한 델리게이트.
    검색어 하이라이팅을 위해 사용합니다.
    """
    def paint(self, painter, option, index):
        options = option
        self.initStyleOption(options, index)

        style = options.widget.style() if options.widget else None
        doc = QTextDocument()
        doc.setHtml(options.text)

        options.text = ""
        style.drawControl(style.CE_ItemViewItem, options, painter, options.widget)

        ctx = QAbstractTextDocumentLayout.PaintContext()
        # [KR] 선택된 항목의 텍스트 색상 조정
        if options.state & style.State_Selected:
            ctx.palette.setColor(QPalette.Text, options.palette.color(QPalette.HighlightedText))
        else:
            ctx.palette.setColor(QPalette.Text, options.palette.color(QPalette.Text))

        painter.save()
        painter.translate(options.rect.topLeft())
        # 수직 중앙 정렬
        painter.translate(0, (options.rect.height() - doc.size().height()) / 2)
        doc.documentLayout().draw(painter, ctx)
        painter.restore()

class ResultTable(QWidget):
    """
    [KR] 검색 결과 표시 위젯.
    검색된 데이터를 테이블 형태로 보여주고 체크박스 선택을 지원합니다.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        self.setLayout(layout)

        # [KR] 결과 내 필터링 (Result Filter)
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Filter in Results:"))
        self.input_filter = QLineEdit()
        self.input_filter.setPlaceholderText("Type to filter visible results...")
        self.input_filter.textChanged.connect(self.filter_results)
        filter_layout.addWidget(self.input_filter)

        self.lbl_title = QLabel("Results Index: 0 found")

        self.table_results = QTableWidget()
        self.table_results.setColumnCount(4)
        self.table_results.setHorizontalHeaderLabels(["[X]", "Source", "Sheet", "Preview (Row Data)"])
        self.table_results.setColumnWidth(0, 30)
        self.table_results.setColumnWidth(1, 150)
        self.table_results.setColumnWidth(2, 100)
        self.table_results.horizontalHeader().setStretchLastSection(True)

        # [KR] HTML 델리게이트 적용 (Preview 컬럼)
        self.table_results.setItemDelegateForColumn(3, HTMLDelegate(self.table_results))

        # [KR] 더블 클릭 및 컨텍스트 메뉴 설정
        self.table_results.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table_results.customContextMenuRequested.connect(self.on_context_menu)
        self.table_results.cellDoubleClicked.connect(self.on_double_click)

        layout.addLayout(filter_layout)
        layout.addWidget(self.lbl_title)
        layout.addWidget(self.table_results)

        self.current_keyword = "" # 하이라이팅용

    def set_keyword(self, keyword):
        self.current_keyword = keyword

    def filter_results(self, text):
        """
        [KR] 결과 내 재검색 (간이 필터링).
        복잡한 ProxyModel 대신, setRowHidden을 사용하여 간단히 구현.
        """
        for i in range(self.table_results.rowCount()):
            visible = False
            # 모든 컬럼 텍스트 검사
            for j in range(1, 4):
                item = self.table_results.item(i, j)
                if item and text.lower() in item.text().lower():
                    visible = True
                    break
            self.table_results.setRowHidden(i, not visible)

    def add_result_row(self, file_name, sheet_name, preview_text, full_path, raw_data):
        row_idx = self.table_results.rowCount()
        self.table_results.insertRow(row_idx)

        # [X] Checkbox Item
        chk_item = QTableWidgetItem()
        chk_item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
        chk_item.setCheckState(Qt.CheckState.Unchecked)
        # [KR] 메타데이터 저장 (UserRole)
        chk_item.setData(Qt.ItemDataRole.UserRole, {
            'full_path': full_path,
            'raw_data': raw_data
        })
        self.table_results.setItem(row_idx, 0, chk_item)

        self.table_results.setItem(row_idx, 1, QTableWidgetItem(file_name))
        self.table_results.setItem(row_idx, 2, QTableWidgetItem(sheet_name))

        # [KR] 하이라이팅 적용
        display_text = preview_text
        if self.current_keyword:
             # 단순 치환으로 하이라이팅 (HTML)
             # 정규식 특수문자 이스케이프 필요할 수 있음. 여기선 단순 구현.
             highlighted = f"<b><font color='red'>{self.current_keyword}</font></b>"
             display_text = preview_text.replace(self.current_keyword, highlighted)

        self.table_results.setItem(row_idx, 3, QTableWidgetItem(display_text))

        self.lbl_title.setText(f"Results Index: {self.table_results.rowCount()} found")

    def clear_results(self):
        self.table_results.setRowCount(0)
        self.lbl_title.setText("Results Index: 0 found")
        self.input_filter.clear()

    def on_double_click(self, row, col):
        """
        [KR] 더블 클릭 시 상세 보기 팝업
        """
        item = self.table_results.item(row, 0)
        data = item.data(Qt.ItemDataRole.UserRole)
        if data and 'raw_data' in data:
            dlg = DetailDialog(data['raw_data'], self)
            dlg.exec()

    def on_context_menu(self, pos):
        """
        [KR] 우클릭 컨텍스트 메뉴 (파일 열기, 폴더 열기)
        """
        item = self.table_results.itemAt(pos)
        if not item:
            return

        row = item.row()
        meta_item = self.table_results.item(row, 0)
        data = meta_item.data(Qt.ItemDataRole.UserRole)

        if not data or 'full_path' not in data:
            return

        full_path = data['full_path']

        menu = QMenu(self)
        action_open_file = QAction("Open File", self)
        action_open_folder = QAction("Open File Location", self)

        action_open_file.triggered.connect(lambda: self.open_file(full_path))
        action_open_folder.triggered.connect(lambda: self.open_folder(full_path))

        menu.addAction(action_open_file)
        menu.addAction(action_open_folder)

        menu.exec(self.table_results.mapToGlobal(pos))

    def open_file(self, path):
        QDesktopServices.openUrl(QUrl.fromLocalFile(path))

    def open_folder(self, path):
        # [KR] 파일의 상위 폴더를 엽니다.
        folder =  QUrl.fromLocalFile(path).adjusted(QUrl.UrlAdjustment.RemoveFilename)
        QDesktopServices.openUrl(folder)

class CopyAction(QWidget):
    """
    [KR] 하단 액션 바 위젯.
    선택된 항목 개수를 표시하고 클립보드 복사, 내보내기 기능을 제공합니다.
    """
    copy_requested = Signal()
    export_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout()
        self.setLayout(layout)

        self.lbl_selected = QLabel("[ Selected: 0 items ]")

        self.btn_export = QPushButton("[ EXPORT RESULTS ]")
        self.btn_export.clicked.connect(self.export_requested.emit)

        self.btn_copy = QPushButton("[ COPY TO CLIPBOARD ]")
        self.btn_copy.clicked.connect(self.copy_requested.emit)

        layout.addWidget(self.lbl_selected)
        layout.addStretch()
        layout.addWidget(self.btn_export)
        layout.addWidget(self.btn_copy)
