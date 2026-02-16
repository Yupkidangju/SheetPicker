"""
[v2.0.0] 메인 윈도우
검색창, 파일 트리, 결과 패널을 조합하여 앱의 전체 레이아웃을 구성합니다.
인덱싱/검색 워커 관리, 테마 전환, 설정 저장/로드를 담당합니다.
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QStatusBar, QLabel, QProgressBar,
    QPushButton, QFileDialog, QApplication
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction
from pathlib import Path

from src.ui.search_bar import SearchBar
from src.ui.file_tree import FileTreePanel
from src.ui.result_cards import ResultPanel
from src.ui.styles import AppStyle, get_dark_stylesheet, get_light_stylesheet
from src.ui.toast import ToastMessage
from src.core.indexer import SearchIndex
from src.core.scanner import FileScanner
from src.core.workers import IndexWorker, SearchWorker
from src.core.cache import IndexCache
from src.utils.config import ConfigManager
from src.utils.clipboard_manager import ClipboardManager
from src.utils.exporter import ResultExporter
from src.utils.logger import logger


class MainWindow(QMainWindow):
    """
    [v2.0.0] Data Scavenger 메인 윈도우.
    좌측 파일 트리 + 우측 검색/결과 영역의 2-패널 레이아웃.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Data Scavenger v2.0")
        self.setMinimumSize(QSize(1000, 650))
        self.resize(1200, 750)

        # 코어 컴포넌트 초기화
        self.search_index = SearchIndex()
        self.cache = IndexCache()
        self._is_dark = True
        self._recent_keywords = []
        self._index_worker = None
        self._search_worker = None

        # 설정 로드
        self._load_config()

        # UI 구성
        self._setup_ui()
        self._setup_statusbar()
        self._connect_signals()

        # 테마 적용
        self._apply_theme()

        logger.info("MainWindow 초기화 완료 (v2.0.0)")

    def _setup_ui(self):
        """UI 레이아웃 구성"""
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(16, 12, 16, 8)
        main_layout.setSpacing(12)

        # 상단: 제목 + 테마 토글
        title_row = QHBoxLayout()
        title_label = QLabel("Data Scavenger")
        title_label.setObjectName("titleLabel")
        title_row.addWidget(title_label)
        title_row.addStretch()

        self.btn_theme = QPushButton("🌙")
        self.btn_theme.setToolTip("테마 전환 (다크/라이트)")
        self.btn_theme.setFixedSize(36, 36)
        self.btn_theme.clicked.connect(self._toggle_theme)
        title_row.addWidget(self.btn_theme)

        main_layout.addLayout(title_row)

        # 검색창
        self.search_bar = SearchBar()
        main_layout.addWidget(self.search_bar)

        # 메인 영역: 좌측 파일 트리 | 우측 결과
        self.splitter = QSplitter(Qt.Horizontal)

        # 좌측 패널
        self.file_tree = FileTreePanel()
        self.file_tree.setMinimumWidth(220)
        self.file_tree.setMaximumWidth(350)
        self.splitter.addWidget(self.file_tree)

        # 우측 패널
        self.result_panel = ResultPanel()
        self.splitter.addWidget(self.result_panel)

        # 스플리터 비율 (좌:우 = 1:3)
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 3)

        main_layout.addWidget(self.splitter, 1)

    def _setup_statusbar(self):
        """하단 상태바 구성"""
        self.statusBar().setStyleSheet("padding: 4px 8px;")
        self.status_label = QLabel("준비됨")
        self.statusBar().addWidget(self.status_label, 1)

        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(200)
        self.progress_bar.setMaximumHeight(12)
        self.progress_bar.setVisible(False)
        self.statusBar().addPermanentWidget(self.progress_bar)

    def _connect_signals(self):
        """시그널-슬롯 연결"""
        # 검색
        self.search_bar.search_requested.connect(self._on_search)

        # 파일 트리
        self.file_tree.files_changed.connect(self._on_files_changed)
        self.file_tree.file_removed.connect(self._on_file_removed)

        # 결과 패널
        self.result_panel.copy_requested.connect(self._on_copy)
        self.result_panel.export_requested.connect(self._on_export)

        # 유사도 슬라이더 변경 시 재검색
        self.result_panel.sim_slider.valueChanged.connect(self._on_similarity_changed)

    # ─── 인덱싱 ───

    def _on_files_changed(self, file_paths: list):
        """파일 목록 변경 시 인덱싱 시작"""
        if not file_paths:
            self.search_index.clear()
            self.search_bar.update_stats(0, 0)
            self.status_label.setText("파일이 제거되었습니다")
            return

        # 기존 인덱싱 중단
        if self._index_worker and self._index_worker.isRunning():
            self._index_worker.stop()
            self._index_worker.wait()

        # 새 파일만 필터링 (이미 인덱싱된 파일 제외)
        new_files = [
            f for f in file_paths
            if f not in self.search_index.indexed_files
        ]

        if not new_files:
            return

        # 인덱싱 워커 시작
        self._index_worker = IndexWorker(new_files, self.search_index, self.cache)
        self._index_worker.progress_updated.connect(self._on_index_progress)
        self._index_worker.indexing_complete.connect(self._on_index_complete)
        self._index_worker.error_occurred.connect(self._on_index_error)
        self.progress_bar.setVisible(True)
        self._index_worker.start()

    def _on_file_removed(self, file_path: str):
        """개별 파일 제거 시 인덱스에서도 제거"""
        self.search_index.remove_file(file_path)
        self.search_bar.update_stats(
            self.search_index.total_files,
            self.search_index.total_rows
        )

    def _on_index_progress(self, msg: str, pct: int):
        """인덱싱 진행 상태 업데이트"""
        self.status_label.setText(msg)
        self.progress_bar.setValue(pct)

    def _on_index_complete(self, file_count: int, row_count: int):
        """인덱싱 완료"""
        self.progress_bar.setVisible(False)
        self.search_bar.update_stats(file_count, row_count)
        self.status_label.setText(
            f"✅ 인덱싱 완료 — {file_count}개 파일, {row_count:,}개 행"
        )

        # 파일 트리에 시트 정보 업데이트
        for (file_path, sheet_name), headers in self.search_index.file_headers.items():
            existing = self.file_tree._files.get(file_path, {})
            sheets = existing.get('sheets', [])
            if sheet_name not in sheets:
                sheets.append(sheet_name)
                self.file_tree.update_sheets(file_path, sheets)

        self.show_toast(f"인덱싱 완료: {file_count}개 파일, {row_count:,}개 행")

    def _on_index_error(self, msg: str):
        """인덱싱 에러"""
        logger.error(msg)
        self.show_toast(f"⚠️ {msg}")

    # ─── 검색 ───

    def _on_search(self, query_text: str):
        """검색 실행"""
        if self.search_index.total_cells == 0:
            self.show_toast("먼저 파일을 추가하고 인덱싱을 완료해 주세요.")
            return

        # 기존 검색 대기
        if self._search_worker and self._search_worker.isRunning():
            self._search_worker.wait()

        min_sim = self.result_panel.get_similarity_threshold()

        self._search_worker = SearchWorker(
            query_text, self.search_index, min_sim
        )
        self._search_worker.results_ready.connect(self._on_results)
        self._search_worker.search_error.connect(self._on_search_error)
        self._search_worker.search_time.connect(self._on_search_time)
        self.status_label.setText(f"검색 중: '{query_text}'...")
        self._search_worker.start()

        # 최근 검색어 추가
        if query_text not in self._recent_keywords:
            self._recent_keywords.insert(0, query_text)
            self._recent_keywords = self._recent_keywords[:10]
            self.search_bar.update_recent(self._recent_keywords)
            ConfigManager.set("recent_keywords", self._recent_keywords)

    def _on_results(self, results):
        """검색 결과 수신"""
        self.result_panel.display_results(results)

    def _on_search_error(self, msg: str):
        """검색 에러"""
        self.status_label.setText(f"검색 오류: {msg}")
        self.show_toast(f"⚠️ 검색 오류: {msg}")

    def _on_search_time(self, elapsed: float):
        """검색 시간 표시"""
        self.status_label.setText(
            f"검색 완료 ({elapsed:.3f}초)"
        )

    def _on_similarity_changed(self, value: int):
        """유사도 슬라이더 변경 시 재검색"""
        current_text = self.search_bar.input.text().strip()
        if current_text and self.search_index.total_cells > 0:
            self._on_search(current_text)

    # ─── 복사 & 내보내기 ───

    def _on_copy(self, results):
        """결과를 클립보드에 복사"""
        rows_data = []
        for r in results:
            row_values = [r.row.cells.get(h, '') for h in r.row.headers]
            rows_data.append(row_values)

        if not rows_data:
            return

        # 헤더 포함
        headers = results[0].row.headers
        formatted = '\t'.join(headers) + '\n'
        formatted += '\n'.join('\t'.join(row) for row in rows_data)

        if ClipboardManager.copy_to_clipboard(formatted):
            self.show_toast(f"📋 {len(results)}건을 클립보드에 복사했습니다")
        else:
            self.show_toast("⚠️ 클립보드 복사에 실패했습니다")

    def _on_export(self, results):
        """결과를 xlsx 파일로 내보내기"""
        if not results:
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "내보내기",
            "검색결과.xlsx",
            "Excel 파일 (*.xlsx);;CSV 파일 (*.csv)"
        )

        if not file_path:
            return

        try:
            ResultExporter.export_results(results, file_path)
            self.show_toast(f"📤 {len(results)}건을 {Path(file_path).name}에 저장했습니다")
        except Exception as e:
            logger.error(f"내보내기 실패: {e}", exc_info=True)
            self.show_toast(f"⚠️ 내보내기 실패: {str(e)}")

    # ─── 테마 ───

    def _toggle_theme(self):
        """다크/라이트 테마 전환"""
        self._is_dark = not self._is_dark
        self._apply_theme()
        ConfigManager.set("is_dark_theme", self._is_dark)

    def _apply_theme(self):
        """현재 테마 적용"""
        app = QApplication.instance()
        if app:
            AppStyle.apply_theme(app, self._is_dark)
        self.btn_theme.setText("☀️" if self._is_dark else "🌙")

    # ─── 설정 ───

    def _load_config(self):
        """설정 로드"""
        self._is_dark = ConfigManager.get("is_dark_theme", True)
        self._recent_keywords = ConfigManager.get("recent_keywords", [])

    # ─── 유틸리티 ───

    def show_toast(self, message: str, duration: int = 3000):
        """토스트 메시지 표시"""
        toast = ToastMessage(message, parent=self, duration=duration)
        toast.show_toast()

    def closeEvent(self, event):
        """앱 종료 시 정리"""
        # 워커 종료
        if self._index_worker and self._index_worker.isRunning():
            self._index_worker.stop()
            self._index_worker.wait()

        # 캐시 연결 닫기
        if self.cache:
            self.cache.close()

        # 설정 저장
        ConfigManager.set("recent_keywords", self._recent_keywords)
        ConfigManager.set("is_dark_theme", self._is_dark)
        ConfigManager.save()

        logger.info("앱 종료")
        event.accept()
