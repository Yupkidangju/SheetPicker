"""
[v2.0.0] 앱 스타일 및 테마 정의
Windows 11 Fluent 디자인을 모방한 모던 다크/라이트 테마를 제공합니다.
"""

from PySide6.QtGui import QPalette, QColor, QFont
from PySide6.QtCore import Qt

# 색상 팔레트 상수
class Colors:
    """앱 전체에서 사용하는 색상 상수"""
    # 다크 테마
    DARK_BG = "#1e1e2e"
    DARK_SURFACE = "#2d2d3f"
    DARK_CARD = "#363649"
    DARK_BORDER = "#45455a"
    DARK_TEXT = "#cdd6f4"
    DARK_SUBTEXT = "#8888a0"
    DARK_INPUT_BG = "#252538"

    # 라이트 테마
    LIGHT_BG = "#f5f5f8"
    LIGHT_SURFACE = "#ffffff"
    LIGHT_CARD = "#ffffff"
    LIGHT_BORDER = "#e0e0e6"
    LIGHT_TEXT = "#1e1e2e"
    LIGHT_SUBTEXT = "#666680"
    LIGHT_INPUT_BG = "#ffffff"

    # 액센트 색상 (테마 공용)
    PRIMARY = "#60cdff"         # Windows 액센트 블루
    EXACT_MATCH = "#6ccb5f"     # 정확 매칭 — 그린
    FUZZY_MATCH = "#f7a93c"     # 유사 매칭 — 오렌지
    CHOSUNG_MATCH = "#b388ff"   # 초성 매칭 — 퍼플
    RANGE_MATCH = "#ff7eb3"     # 범위 매칭 — 핑크
    ERROR = "#f38ba8"           # 에러 — 레드
    SUCCESS = "#a6e3a1"         # 성공 — 그린

    @staticmethod
    def match_color(match_type: str) -> str:
        """매칭 유형에 따른 색상 반환"""
        return {
            'exact': Colors.EXACT_MATCH,
            'fuzzy': Colors.FUZZY_MATCH,
            'chosung': Colors.CHOSUNG_MATCH,
            'range': Colors.RANGE_MATCH,
        }.get(match_type, Colors.PRIMARY)

    @staticmethod
    def match_label(match_type: str) -> str:
        """매칭 유형에 따른 한국어 라벨 반환"""
        return {
            'exact': '정확',
            'fuzzy': '유사',
            'chosung': '초성',
            'range': '범위',
        }.get(match_type, '기타')


def get_dark_stylesheet() -> str:
    """다크 테마 QSS 반환"""
    return f"""
        /* 전역 기본 */
        QMainWindow, QWidget {{
            background-color: {Colors.DARK_BG};
            color: {Colors.DARK_TEXT};
            font-family: 'Pretendard', 'Malgun Gothic', 'Segoe UI', sans-serif;
            font-size: 13px;
        }}

        /* 스크롤바 */
        QScrollBar:vertical {{
            background: {Colors.DARK_BG};
            width: 8px;
            border: none;
        }}
        QScrollBar::handle:vertical {{
            background: {Colors.DARK_BORDER};
            border-radius: 4px;
            min-height: 30px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: {Colors.DARK_SUBTEXT};
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0;
        }}
        QScrollBar:horizontal {{
            background: {Colors.DARK_BG};
            height: 8px;
            border: none;
        }}
        QScrollBar::handle:horizontal {{
            background: {Colors.DARK_BORDER};
            border-radius: 4px;
            min-width: 30px;
        }}

        /* 입력 필드 */
        QLineEdit {{
            background-color: {Colors.DARK_INPUT_BG};
            border: 1px solid {Colors.DARK_BORDER};
            border-radius: 8px;
            padding: 10px 16px;
            font-size: 15px;
            color: {Colors.DARK_TEXT};
            selection-background-color: {Colors.PRIMARY};
        }}
        QLineEdit:focus {{
            border: 2px solid {Colors.PRIMARY};
        }}

        /* 버튼 */
        QPushButton {{
            background-color: {Colors.DARK_SURFACE};
            border: 1px solid {Colors.DARK_BORDER};
            border-radius: 6px;
            padding: 8px 16px;
            color: {Colors.DARK_TEXT};
            font-weight: 500;
        }}
        QPushButton:hover {{
            background-color: {Colors.DARK_CARD};
            border-color: {Colors.PRIMARY};
        }}
        QPushButton:pressed {{
            background-color: {Colors.DARK_BORDER};
        }}
        QPushButton#primaryBtn {{
            background-color: {Colors.PRIMARY};
            color: #1e1e2e;
            border: none;
            font-weight: bold;
        }}
        QPushButton#primaryBtn:hover {{
            background-color: #7dd8ff;
        }}

        /* 트리 위젯 */
        QTreeWidget {{
            background-color: {Colors.DARK_SURFACE};
            border: 1px solid {Colors.DARK_BORDER};
            border-radius: 8px;
            padding: 4px;
            outline: none;
        }}
        QTreeWidget::item {{
            padding: 4px 8px;
            border-radius: 4px;
        }}
        QTreeWidget::item:hover {{
            background-color: {Colors.DARK_CARD};
        }}
        QTreeWidget::item:selected {{
            background-color: {Colors.PRIMARY};
            color: #1e1e2e;
        }}
        QTreeWidget::branch {{
            background: transparent;
        }}

        /* 테이블 위젯 */
        QTableWidget {{
            background-color: {Colors.DARK_SURFACE};
            border: none;
            border-radius: 6px;
            gridline-color: {Colors.DARK_BORDER};
            selection-background-color: {Colors.PRIMARY};
            selection-color: #1e1e2e;
        }}
        QHeaderView::section {{
            background-color: {Colors.DARK_CARD};
            color: {Colors.DARK_SUBTEXT};
            border: none;
            border-bottom: 1px solid {Colors.DARK_BORDER};
            padding: 8px;
            font-weight: bold;
            font-size: 12px;
        }}

        /* 체크박스 */
        QCheckBox {{
            spacing: 8px;
            color: {Colors.DARK_TEXT};
        }}
        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
            border-radius: 4px;
            border: 2px solid {Colors.DARK_BORDER};
            background-color: {Colors.DARK_INPUT_BG};
        }}
        QCheckBox::indicator:checked {{
            background-color: {Colors.PRIMARY};
            border-color: {Colors.PRIMARY};
        }}

        /* 콤보박스 */
        QComboBox {{
            background-color: {Colors.DARK_INPUT_BG};
            border: 1px solid {Colors.DARK_BORDER};
            border-radius: 6px;
            padding: 6px 12px;
            color: {Colors.DARK_TEXT};
        }}

        /* 슬라이더 */
        QSlider::groove:horizontal {{
            height: 4px;
            background: {Colors.DARK_BORDER};
            border-radius: 2px;
        }}
        QSlider::handle:horizontal {{
            background: {Colors.PRIMARY};
            width: 16px;
            height: 16px;
            margin: -6px 0;
            border-radius: 8px;
        }}
        QSlider::sub-page:horizontal {{
            background: {Colors.PRIMARY};
            border-radius: 2px;
        }}

        /* 상태바 */
        QStatusBar {{
            background-color: {Colors.DARK_SURFACE};
            color: {Colors.DARK_SUBTEXT};
            border-top: 1px solid {Colors.DARK_BORDER};
            font-size: 12px;
        }}

        /* 그룹박스 */
        QGroupBox {{
            border: 1px solid {Colors.DARK_BORDER};
            border-radius: 8px;
            margin-top: 12px;
            padding-top: 16px;
            color: {Colors.DARK_TEXT};
            font-weight: bold;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: 12px;
            padding: 0 6px;
        }}

        /* 라벨 */
        QLabel#subtextLabel {{
            color: {Colors.DARK_SUBTEXT};
            font-size: 12px;
        }}
        QLabel#titleLabel {{
            font-size: 18px;
            font-weight: bold;
            color: {Colors.DARK_TEXT};
        }}

        /* 스플리터 */
        QSplitter::handle {{
            background-color: {Colors.DARK_BORDER};
            width: 1px;
        }}

        /* 프로그레스바 */
        QProgressBar {{
            border: none;
            background-color: {Colors.DARK_BORDER};
            border-radius: 3px;
            height: 6px;
            text-align: center;
        }}
        QProgressBar::chunk {{
            background-color: {Colors.PRIMARY};
            border-radius: 3px;
        }}

        /* 툴팁 */
        QToolTip {{
            background-color: {Colors.DARK_CARD};
            color: {Colors.DARK_TEXT};
            border: 1px solid {Colors.DARK_BORDER};
            border-radius: 4px;
            padding: 6px;
        }}
    """


def get_light_stylesheet() -> str:
    """라이트 테마 QSS 반환"""
    return f"""
        QMainWindow, QWidget {{
            background-color: {Colors.LIGHT_BG};
            color: {Colors.LIGHT_TEXT};
            font-family: 'Pretendard', 'Malgun Gothic', 'Segoe UI', sans-serif;
            font-size: 13px;
        }}
        QScrollBar:vertical {{
            background: {Colors.LIGHT_BG};
            width: 8px;
            border: none;
        }}
        QScrollBar::handle:vertical {{
            background: {Colors.LIGHT_BORDER};
            border-radius: 4px;
            min-height: 30px;
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0;
        }}
        QLineEdit {{
            background-color: {Colors.LIGHT_INPUT_BG};
            border: 1px solid {Colors.LIGHT_BORDER};
            border-radius: 8px;
            padding: 10px 16px;
            font-size: 15px;
            color: {Colors.LIGHT_TEXT};
        }}
        QLineEdit:focus {{
            border: 2px solid {Colors.PRIMARY};
        }}
        QPushButton {{
            background-color: {Colors.LIGHT_SURFACE};
            border: 1px solid {Colors.LIGHT_BORDER};
            border-radius: 6px;
            padding: 8px 16px;
            color: {Colors.LIGHT_TEXT};
            font-weight: 500;
        }}
        QPushButton:hover {{
            background-color: #e8e8f0;
            border-color: {Colors.PRIMARY};
        }}
        QPushButton#primaryBtn {{
            background-color: #0078d4;
            color: white;
            border: none;
            font-weight: bold;
        }}
        QTreeWidget {{
            background-color: {Colors.LIGHT_SURFACE};
            border: 1px solid {Colors.LIGHT_BORDER};
            border-radius: 8px;
            padding: 4px;
        }}
        QTreeWidget::item {{
            padding: 4px 8px;
            border-radius: 4px;
        }}
        QTreeWidget::item:selected {{
            background-color: #0078d4;
            color: white;
        }}
        QTableWidget {{
            background-color: {Colors.LIGHT_SURFACE};
            border: none;
            border-radius: 6px;
            gridline-color: {Colors.LIGHT_BORDER};
        }}
        QHeaderView::section {{
            background-color: {Colors.LIGHT_BG};
            color: {Colors.LIGHT_SUBTEXT};
            border: none;
            border-bottom: 1px solid {Colors.LIGHT_BORDER};
            padding: 8px;
            font-weight: bold;
            font-size: 12px;
        }}
        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
            border-radius: 4px;
            border: 2px solid {Colors.LIGHT_BORDER};
        }}
        QCheckBox::indicator:checked {{
            background-color: #0078d4;
            border-color: #0078d4;
        }}
        QSlider::groove:horizontal {{
            height: 4px;
            background: {Colors.LIGHT_BORDER};
            border-radius: 2px;
        }}
        QSlider::handle:horizontal {{
            background: #0078d4;
            width: 16px;
            height: 16px;
            margin: -6px 0;
            border-radius: 8px;
        }}
        QStatusBar {{
            background-color: {Colors.LIGHT_SURFACE};
            color: {Colors.LIGHT_SUBTEXT};
            border-top: 1px solid {Colors.LIGHT_BORDER};
        }}
        QSplitter::handle {{
            background-color: {Colors.LIGHT_BORDER};
            width: 1px;
        }}
        QProgressBar {{
            border: none;
            background-color: {Colors.LIGHT_BORDER};
            border-radius: 3px;
            height: 6px;
        }}
        QProgressBar::chunk {{
            background-color: #0078d4;
            border-radius: 3px;
        }}
        QLabel#subtextLabel {{
            color: {Colors.LIGHT_SUBTEXT};
            font-size: 12px;
        }}
        QLabel#titleLabel {{
            font-size: 18px;
            font-weight: bold;
        }}
        QToolTip {{
            background-color: white;
            color: {Colors.LIGHT_TEXT};
            border: 1px solid {Colors.LIGHT_BORDER};
            padding: 6px;
        }}
    """


class AppStyle:
    """앱 테마 관리 클래스"""

    @staticmethod
    def apply_theme(app, is_dark: bool = True):
        """다크/라이트 테마를 적용합니다. 기본은 다크 모드."""
        if is_dark:
            app.setStyleSheet(get_dark_stylesheet())
        else:
            app.setStyleSheet(get_light_stylesheet())
