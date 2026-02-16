"""
[v2.0.0] 검색 결과 카드 패널
파일/시트별로 그룹핑된 카드 형태로 검색 결과를 표시합니다.
체크박스 선택, 전체 선택, 복사, 내보내기를 지원합니다.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QTableWidget, QTableWidgetItem,
    QCheckBox, QHeaderView, QSlider, QAbstractItemView,
    QSizePolicy
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QColor
from typing import List, Dict
from collections import defaultdict
from src.core.searcher import SearchResult
from src.ui.styles import Colors


class MatchTag(QLabel):
    """매칭 유형을 색상 태그로 표시하는 위젯"""

    def __init__(self, match_type: str, similarity: float = 1.0, parent=None):
        super().__init__(parent)
        color = Colors.match_color(match_type)
        label = Colors.match_label(match_type)

        if match_type == 'fuzzy':
            text = f"{label} {int(similarity * 100)}%"
        else:
            text = label

        self.setText(text)
        self.setStyleSheet(f"""
            background-color: {color};
            color: #1e1e2e;
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 11px;
            font-weight: bold;
        """)
        self.setFixedHeight(20)


class ResultCard(QFrame):
    """
    파일/시트 단위 결과 카드.
    헤더에 파일명/시트명, 매칭 유형별 건수를 표시하고
    내부에 결과 행 테이블을 포함합니다.
    """

    def __init__(self, file_name: str, sheet_name: str,
                 results: List[SearchResult], parent=None):
        super().__init__(parent)
        self.results = results
        self._checked_rows = set()
        self._setup_ui(file_name, sheet_name)

    def _setup_ui(self, file_name: str, sheet_name: str):
        self.setObjectName("resultCard")
        self.setStyleSheet(f"""
            QFrame#resultCard {{
                background-color: {Colors.DARK_SURFACE};
                border: 1px solid {Colors.DARK_BORDER};
                border-radius: 10px;
                padding: 0px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)

        # 카드 헤더: 파일명 + 매칭 통계
        header_row = QHBoxLayout()
        title = QLabel(f"📄 {file_name} › {sheet_name}")
        title.setStyleSheet("font-weight: bold; font-size: 13px;")
        header_row.addWidget(title)
        header_row.addStretch()

        # 매칭 유형별 건수 태그
        type_counts = defaultdict(int)
        for r in self.results:
            type_counts[r.match_type] += 1

        for mtype, count in type_counts.items():
            tag = MatchTag(mtype, self.results[0].similarity if mtype == 'fuzzy' else 1.0)
            tag.setText(f"{Colors.match_label(mtype)} {count}건")
            header_row.addWidget(tag)

        layout.addLayout(header_row)

        # 결과 테이블
        if not self.results:
            return

        first_row = self.results[0].row
        headers = first_row.headers
        display_headers = [""] + headers  # 첫 열은 체크박스

        self.table = QTableWidget(len(self.results), len(display_headers))
        self.table.setHorizontalHeaderLabels(display_headers)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)

        # 체크박스 열 너비 고정
        self.table.setColumnWidth(0, 30)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        for col_idx in range(1, len(display_headers)):
            self.table.horizontalHeader().setSectionResizeMode(
                col_idx, QHeaderView.Stretch
            )

        # 테이블에 데이터 채우기
        for row_idx, result in enumerate(self.results):
            # 체크박스
            cb = QCheckBox()
            cb.stateChanged.connect(
                lambda state, idx=row_idx: self._on_check_changed(idx, state)
            )
            self.table.setCellWidget(row_idx, 0, cb)

            # 데이터 셀
            for col_idx, col_name in enumerate(headers):
                value = result.row.cells.get(col_name, '')
                item = QTableWidgetItem(value)

                # 매칭된 셀 강조
                is_matched = any(
                    m.col_name == col_name for m in result.matches
                )
                if is_matched:
                    match_color = Colors.match_color(result.match_type)
                    item.setForeground(QColor(match_color))
                    item.setFont(item.font())
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)

                self.table.setItem(row_idx, col_idx + 1, item)

        # 테이블 높이 자동 조절 (최대 300px)
        row_height = 30
        table_height = min(
            len(self.results) * row_height + 35,  # 헤더 높이 포함
            300
        )
        self.table.setMinimumHeight(table_height)
        self.table.setMaximumHeight(table_height)

        layout.addWidget(self.table)

    def _on_check_changed(self, row_idx: int, state: int):
        if state == Qt.Checked.value:
            self._checked_rows.add(row_idx)
        else:
            self._checked_rows.discard(row_idx)

    def get_checked_results(self) -> List[SearchResult]:
        """체크된 결과만 반환"""
        return [self.results[i] for i in self._checked_rows]

    def get_all_results(self) -> List[SearchResult]:
        """모든 결과 반환"""
        return self.results

    def select_all(self, checked: bool):
        """전체 선택/해제"""
        for row_idx in range(self.table.rowCount()):
            cb = self.table.cellWidget(row_idx, 0)
            if cb:
                cb.setChecked(checked)


class ResultPanel(QWidget):
    """
    [v2.0.0] 검색 결과 패널.
    - 스크롤 영역에 파일/시트별 카드를 배치
    - 유사도 슬라이더로 필터링
    - 전체 선택, 복사, 내보내기 버튼
    """

    export_requested = Signal(list)  # List[SearchResult]
    copy_requested = Signal(list)    # List[SearchResult]

    def __init__(self, parent=None):
        super().__init__(parent)
        self._cards: List[ResultCard] = []
        self._all_results: List[SearchResult] = []
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # 상단 바: 결과 건수 + 유사도 슬라이더
        top_row = QHBoxLayout()

        self.result_count_label = QLabel("검색 결과")
        self.result_count_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        top_row.addWidget(self.result_count_label)
        top_row.addStretch()

        # 유사도 필터 슬라이더
        sim_label = QLabel("유사도:")
        sim_label.setObjectName("subtextLabel")
        top_row.addWidget(sim_label)

        self.sim_slider = QSlider(Qt.Horizontal)
        self.sim_slider.setRange(40, 100)
        self.sim_slider.setValue(60)
        self.sim_slider.setMaximumWidth(150)
        self.sim_slider.setToolTip("최소 유사도 임계값")
        top_row.addWidget(self.sim_slider)

        self.sim_value_label = QLabel("60%")
        self.sim_value_label.setObjectName("subtextLabel")
        self.sim_value_label.setMinimumWidth(35)
        top_row.addWidget(self.sim_value_label)

        self.sim_slider.valueChanged.connect(
            lambda v: self.sim_value_label.setText(f"{v}%")
        )

        layout.addLayout(top_row)

        # 스크롤 영역 (카드 배치)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)

        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setSpacing(12)
        self.scroll_layout.setContentsMargins(0, 0, 8, 0)
        self.scroll_layout.addStretch()

        self.scroll_area.setWidget(self.scroll_content)
        layout.addWidget(self.scroll_area, 1)

        # 하단 컨트롤 바
        bottom_row = QHBoxLayout()

        self.cb_select_all = QCheckBox("전체 선택")
        self.cb_select_all.stateChanged.connect(self._on_select_all)
        bottom_row.addWidget(self.cb_select_all)

        bottom_row.addStretch()

        self.btn_copy = QPushButton("📋 복사")
        self.btn_copy.setToolTip("선택된 항목을 클립보드에 복사합니다")
        self.btn_copy.clicked.connect(self._on_copy)
        bottom_row.addWidget(self.btn_copy)

        self.btn_export = QPushButton("📤 내보내기 (xlsx)")
        self.btn_export.setObjectName("primaryBtn")
        self.btn_export.setToolTip("선택된 항목을 Excel 파일로 저장합니다")
        self.btn_export.clicked.connect(self._on_export)
        bottom_row.addWidget(self.btn_export)

        layout.addLayout(bottom_row)

    def display_results(self, results: List[SearchResult]):
        """검색 결과를 카드로 표시합니다."""
        self._all_results = results
        self._clear_cards()

        if not results:
            self.result_count_label.setText("검색 결과 없음")
            no_result_label = QLabel("검색 결과가 없습니다. 다른 키워드를 시도해 보세요.")
            no_result_label.setAlignment(Qt.AlignCenter)
            no_result_label.setObjectName("subtextLabel")
            no_result_label.setStyleSheet("padding: 40px; font-size: 14px;")
            self.scroll_layout.insertWidget(0, no_result_label)
            return

        # 결과를 파일/시트별로 그룹핑
        groups: Dict[tuple, List[SearchResult]] = defaultdict(list)
        for r in results:
            key = (r.row.file_name, r.row.sheet_name)
            groups[key].append(r)

        # 카드 생성
        total_exact = sum(1 for r in results if r.match_type == 'exact')
        total_fuzzy = sum(1 for r in results if r.match_type == 'fuzzy')
        total_chosung = sum(1 for r in results if r.match_type == 'chosung')
        total_range = sum(1 for r in results if r.match_type == 'range')

        stats = f"검색 결과 ({len(results)}건)"
        if total_exact:
            stats += f" | 정확 {total_exact}"
        if total_fuzzy:
            stats += f" | 유사 {total_fuzzy}"
        if total_chosung:
            stats += f" | 초성 {total_chosung}"
        if total_range:
            stats += f" | 범위 {total_range}"
        self.result_count_label.setText(stats)

        for (file_name, sheet_name), group_results in groups.items():
            card = ResultCard(file_name, sheet_name, group_results)
            self._cards.append(card)
            # stretch 앞에 삽입
            self.scroll_layout.insertWidget(
                self.scroll_layout.count() - 1, card
            )

        self.cb_select_all.setChecked(False)

    def get_similarity_threshold(self) -> float:
        """유사도 슬라이더 값을 0.0~1.0으로 반환"""
        return self.sim_slider.value() / 100.0

    def _clear_cards(self):
        """기존 카드 제거"""
        for card in self._cards:
            self.scroll_layout.removeWidget(card)
            card.deleteLater()
        self._cards.clear()

        # 결과 없음 라벨 제거
        for i in range(self.scroll_layout.count() - 1):
            item = self.scroll_layout.itemAt(i)
            if item and item.widget():
                item.widget().deleteLater()

    def _on_select_all(self, state):
        checked = state == Qt.Checked.value
        for card in self._cards:
            card.select_all(checked)

    def _get_selected_results(self) -> List[SearchResult]:
        """체크된 결과를 반환. 체크된 것이 없으면 전체 반환."""
        checked = []
        for card in self._cards:
            checked.extend(card.get_checked_results())
        return checked if checked else self._all_results

    def _on_copy(self):
        results = self._get_selected_results()
        if results:
            self.copy_requested.emit(results)

    def _on_export(self):
        results = self._get_selected_results()
        if results:
            self.export_requested.emit(results)
