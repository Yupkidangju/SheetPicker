"""
[v2.0.0] 파일 트리 패널
좌측 사이드바에 파일/시트 트리를 표시하고, 즐겨찾기(파일 세트) 관리를 제공합니다.
파일 추가/제거, 드래그&드롭, 즐겨찾기 저장/로드를 지원합니다.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTreeWidget, QTreeWidgetItem, QFileDialog, QMenu,
    QInputDialog, QComboBox, QFrame, QMessageBox
)
from PySide6.QtCore import Signal, Qt, QUrl
from PySide6.QtGui import QAction
from pathlib import Path
from src.core.scanner import FileScanner
from src.utils.config import ConfigManager


class FileTreePanel(QWidget):
    """
    [v2.0.0] 파일 트리 사이드바.
    - 파일/폴더 추가 (버튼 + 드래그&드롭)
    - 트리 뷰로 파일/시트 구조 표시
    - 즐겨찾기: 파일 세트를 이름 붙여 저장/복원
    - 파일 변경 시 시그널로 메인 윈도우에 통지
    """

    files_changed = Signal(list)      # 현재 파일 목록 변경 시
    file_removed = Signal(str)        # 개별 파일 제거 시

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self._files = {}  # file_path → {name, sheets}
        self._scanner = FileScanner()
        self._setup_ui()
        self._load_favorites()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # 헤더
        header = QLabel("📁 파일")
        header.setObjectName("titleLabel")
        header.setStyleSheet("font-size: 16px;")
        layout.addWidget(header)

        # 파일 트리
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self._on_context_menu)
        self.tree.setMinimumWidth(200)
        layout.addWidget(self.tree, 1)

        # 파일 추가 버튼
        btn_row = QHBoxLayout()
        btn_row.setSpacing(4)

        self.btn_add_file = QPushButton("+ 파일")
        self.btn_add_file.setToolTip("Excel/CSV 파일을 추가합니다")
        self.btn_add_file.clicked.connect(self._on_add_files)

        self.btn_add_folder = QPushButton("+ 폴더")
        self.btn_add_folder.setToolTip("폴더 내 모든 Excel/CSV 파일을 추가합니다")
        self.btn_add_folder.clicked.connect(self._on_add_folder)

        btn_row.addWidget(self.btn_add_file)
        btn_row.addWidget(self.btn_add_folder)
        layout.addLayout(btn_row)

        # 전체 제거 버튼
        self.btn_clear = QPushButton("전체 제거")
        self.btn_clear.clicked.connect(self._on_clear_all)
        layout.addWidget(self.btn_clear)

        # 구분선
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color: #45455a;")
        layout.addWidget(sep)

        # 즐겨찾기 섹션
        fav_label = QLabel("⭐ 즐겨찾기 (파일 세트)")
        fav_label.setObjectName("subtextLabel")
        fav_label.setStyleSheet("font-weight: bold; font-size: 13px;")
        layout.addWidget(fav_label)

        self.combo_favorites = QComboBox()
        self.combo_favorites.setPlaceholderText("저장된 세트 선택...")
        layout.addWidget(self.combo_favorites)

        fav_btn_row = QHBoxLayout()
        fav_btn_row.setSpacing(4)

        self.btn_save_fav = QPushButton("세트 저장")
        self.btn_save_fav.setToolTip("현재 파일 목록을 즐겨찾기로 저장합니다")
        self.btn_save_fav.clicked.connect(self._on_save_favorite)

        self.btn_load_fav = QPushButton("세트 불러오기")
        self.btn_load_fav.setToolTip("저장된 파일 세트를 불러옵니다")
        self.btn_load_fav.clicked.connect(self._on_load_favorite)

        self.btn_delete_fav = QPushButton("삭제")
        self.btn_delete_fav.setToolTip("선택된 즐겨찾기를 삭제합니다")
        self.btn_delete_fav.clicked.connect(self._on_delete_favorite)

        fav_btn_row.addWidget(self.btn_save_fav)
        fav_btn_row.addWidget(self.btn_load_fav)
        fav_btn_row.addWidget(self.btn_delete_fav)
        layout.addLayout(fav_btn_row)

    # ─── 파일 관리 ───

    def add_files(self, file_paths: list):
        """파일 경로 리스트를 추가합니다."""
        new_files = []
        for fp in file_paths:
            fp = str(Path(fp).resolve())
            if fp not in self._files:
                name = Path(fp).name
                self._files[fp] = {'name': name, 'sheets': []}
                new_files.append(fp)

        if new_files:
            self._refresh_tree()
            self.files_changed.emit(list(self._files.keys()))

    def remove_file(self, file_path: str):
        """파일을 목록에서 제거합니다."""
        if file_path in self._files:
            del self._files[file_path]
            self._refresh_tree()
            self.file_removed.emit(file_path)
            self.files_changed.emit(list(self._files.keys()))

    def update_sheets(self, file_path: str, sheets: list):
        """파일의 시트 목록을 업데이트합니다 (인덱싱 완료 후)."""
        if file_path in self._files:
            self._files[file_path]['sheets'] = sheets
            self._refresh_tree()

    def get_all_files(self) -> list:
        """현재 등록된 모든 파일 경로를 반환합니다."""
        return list(self._files.keys())

    def _refresh_tree(self):
        """트리 위젯을 재구성합니다."""
        self.tree.clear()
        for fp, info in self._files.items():
            file_item = QTreeWidgetItem([f"📄 {info['name']}"])
            file_item.setData(0, Qt.UserRole, fp)
            file_item.setToolTip(0, fp)

            for sheet_name in info.get('sheets', []):
                sheet_item = QTreeWidgetItem([f"  └ {sheet_name}"])
                sheet_item.setData(0, Qt.UserRole, f"{fp}::{sheet_name}")
                file_item.addChild(sheet_item)

            self.tree.addTopLevelItem(file_item)

        self.tree.expandAll()

    # ─── 이벤트 핸들러 ───

    def _on_add_files(self):
        """파일 추가 다이얼로그"""
        files, _ = QFileDialog.getOpenFileNames(
            self, "파일 추가",
            "",
            "Excel/CSV 파일 (*.xlsx *.xls *.csv);;모든 파일 (*.*)"
        )
        if files:
            self.add_files(files)

    def _on_add_folder(self):
        """폴더 추가 다이얼로그"""
        folder = QFileDialog.getExistingDirectory(self, "폴더 선택")
        if folder:
            found = self._scanner.get_supported_files([folder])
            if found:
                self.add_files(found)

    def _on_clear_all(self):
        """모든 파일 제거"""
        self._files.clear()
        self._refresh_tree()
        self.files_changed.emit([])

    def _on_context_menu(self, pos):
        """트리 아이템 우클릭 메뉴"""
        item = self.tree.itemAt(pos)
        if item is None:
            return

        file_path = item.data(0, Qt.UserRole)
        if '::' in str(file_path):
            return  # 시트 아이템은 메뉴 미제공

        menu = QMenu(self)
        action_remove = menu.addAction("제거")
        action_open = menu.addAction("파일 열기")
        action_folder = menu.addAction("폴더 열기")

        action = menu.exec(self.tree.viewport().mapToGlobal(pos))
        if action == action_remove:
            self.remove_file(file_path)
        elif action == action_open:
            from PySide6.QtGui import QDesktopServices
            QDesktopServices.openUrl(QUrl.fromLocalFile(file_path))
        elif action == action_folder:
            from PySide6.QtGui import QDesktopServices
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(Path(file_path).parent)))

    # ─── 드래그 & 드롭 ───

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        paths = [url.toLocalFile() for url in urls]
        # 폴더와 파일을 구분하여 처리
        all_files = self._scanner.get_supported_files(paths)
        if all_files:
            self.add_files(all_files)
            event.acceptProposedAction()

    # ─── 즐겨찾기 (파일 세트 저장/복원) ───

    def _load_favorites(self):
        """설정에서 즐겨찾기 목록을 로드합니다."""
        favorites = ConfigManager.get("file_set_favorites", {})
        self.combo_favorites.clear()
        for name in favorites.keys():
            self.combo_favorites.addItem(name)

    def _on_save_favorite(self):
        """현재 파일 목록을 즐겨찾기로 저장합니다."""
        if not self._files:
            return

        name, ok = QInputDialog.getText(
            self, "파일 세트 저장", "세트 이름을 입력하세요:"
        )
        if ok and name:
            favorites = ConfigManager.get("file_set_favorites", {})
            favorites[name] = list(self._files.keys())
            ConfigManager.set("file_set_favorites", favorites)
            self._load_favorites()
            self.combo_favorites.setCurrentText(name)

    def _on_load_favorite(self):
        """저장된 파일 세트를 불러와 추가합니다."""
        name = self.combo_favorites.currentText()
        if not name:
            return

        favorites = ConfigManager.get("file_set_favorites", {})
        file_list = favorites.get(name, [])

        # 존재하는 파일만 필터링
        existing = [f for f in file_list if Path(f).exists()]
        missing = len(file_list) - len(existing)

        if existing:
            self.add_files(existing)

        if missing > 0:
            QMessageBox.information(
                self, "알림",
                f"{missing}개 파일이 더 이상 존재하지 않아 건너뛰었습니다."
            )

    def _on_delete_favorite(self):
        """선택된 즐겨찾기를 삭제합니다."""
        name = self.combo_favorites.currentText()
        if not name:
            return

        favorites = ConfigManager.get("file_set_favorites", {})
        if name in favorites:
            del favorites[name]
            ConfigManager.set("file_set_favorites", favorites)
            self._load_favorites()
