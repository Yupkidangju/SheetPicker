"""
[v2.0.0] 구글 스타일 검색창 위젯
단일 입력창으로 모든 검색을 처리합니다.
디바운스(300ms)로 타이핑이 끝나면 자동 검색을 트리거합니다.
"""

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLineEdit,
    QPushButton, QLabel, QFrame
)
from PySide6.QtCore import Signal, Qt, QTimer
from PySide6.QtGui import QKeySequence, QShortcut
from src.ui.styles import Colors


class SearchBar(QWidget):
    """
    [v2.0.0] 단일 검색창 위젯.
    - 검색어 입력 시 300ms 디바운스 후 자동 검색 시그널 방출
    - 최근 검색어 태그 표시
    - 파일 통계 라벨
    """

    # 시그널: 검색어 문자열 전달
    search_requested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._setup_debounce()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # 검색 입력 영역
        search_row = QHBoxLayout()
        search_row.setSpacing(8)

        # 검색 아이콘 + 입력창
        self.input = QLineEdit()
        self.input.setPlaceholderText("🔍  검색어를 입력하세요...")
        self.input.setClearButtonEnabled(True)
        self.input.setMinimumHeight(44)
        self.input.returnPressed.connect(self._emit_search_now)

        # 검색 버튼
        self.btn_search = QPushButton("검색")
        self.btn_search.setObjectName("primaryBtn")
        self.btn_search.setMinimumHeight(44)
        self.btn_search.setMinimumWidth(80)
        self.btn_search.clicked.connect(self._emit_search_now)

        search_row.addWidget(self.input, 1)
        search_row.addWidget(self.btn_search)
        layout.addLayout(search_row)

        # 하단 정보 바: 최근 검색어 + 파일 통계
        info_row = QHBoxLayout()
        info_row.setSpacing(8)

        self.recent_label = QLabel("")
        self.recent_label.setObjectName("subtextLabel")
        self.recent_label.setWordWrap(True)

        self.stats_label = QLabel("파일을 추가해 주세요")
        self.stats_label.setObjectName("subtextLabel")
        self.stats_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        info_row.addWidget(self.recent_label, 1)
        info_row.addWidget(self.stats_label)
        layout.addLayout(info_row)

    def _setup_debounce(self):
        """300ms 디바운스 타이머 설정"""
        self.debounce_timer = QTimer(self)
        self.debounce_timer.setSingleShot(True)
        self.debounce_timer.setInterval(300)
        self.debounce_timer.timeout.connect(self._emit_search)
        self.input.textChanged.connect(self._on_text_changed)

    def _on_text_changed(self, text: str):
        """텍스트 변경 시 디바운스 타이머 리셋"""
        if text.strip():
            self.debounce_timer.start()
        else:
            self.debounce_timer.stop()

    def _emit_search(self):
        """디바운스 후 검색 시그널 방출"""
        text = self.input.text().strip()
        if text:
            self.search_requested.emit(text)

    def _emit_search_now(self):
        """즉시 검색 (엔터 키 또는 버튼 클릭)"""
        self.debounce_timer.stop()
        text = self.input.text().strip()
        if text:
            self.search_requested.emit(text)

    def update_stats(self, file_count: int, row_count: int):
        """파일/행 통계 업데이트"""
        if file_count == 0:
            self.stats_label.setText("파일을 추가해 주세요")
        else:
            self.stats_label.setText(f"{file_count}개 파일, {row_count:,}개 행 로드됨")

    def update_recent(self, recent_keywords: list):
        """최근 검색어를 태그 형태로 표시"""
        if not recent_keywords:
            self.recent_label.setText("")
            return
        tags = " ".join([f"[{kw}]" for kw in recent_keywords[:8]])
        self.recent_label.setText(f"최근: {tags}")

    def set_text(self, text: str):
        """외부에서 검색어를 설정"""
        self.input.setText(text)

    def clear(self):
        """검색창 초기화"""
        self.input.clear()
