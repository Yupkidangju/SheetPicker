from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt

class AppStyle:
    """
    [KR] 애플리케이션 스타일 및 테마 정의 클래스.
    """

    @staticmethod
    def apply_theme(app, is_dark: bool = False):
        """
        [KR] 다크 모드 또는 라이트 모드 테마를 적용합니다.
        """
        if is_dark:
            AppStyle._apply_dark_theme(app)
        else:
            AppStyle._apply_light_theme(app)

    @staticmethod
    def _apply_dark_theme(app):
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ToolTipBase, Qt.white)
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, Qt.black)
        app.setPalette(palette)

        # [KR] 위젯별 QSS 추가 (다크)
        app.setStyleSheet("""
            QToolTip { color: #ffffff; background-color: #2a82da; border: 1px solid white; }
            QGroupBox { border: 1px solid #777; margin-top: 1ex; border-radius: 4px; color: white; }
            QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 3px; }
            QPushButton { background-color: #444; border: 1px solid #666; padding: 5px; border-radius: 4px; color: white; }
            QPushButton:hover { background-color: #555; }
            QPushButton:pressed { background-color: #333; }
            QTableWidget { gridline-color: #555; }
            QHeaderView::section { background-color: #444; color: white; border: 1px solid #555; padding: 4px; }
            QLineEdit, QComboBox { padding: 4px; border-radius: 4px; background-color: #333; color: white; border: 1px solid #555; }
            QListWidget { background-color: #333; color: white; border: 1px solid #555; border-radius: 4px; }
        """)

    @staticmethod
    def _apply_light_theme(app):
        # [KR] 기본 윈도우 스타일 복원 (시스템 테마 따름)
        app.setPalette(QPalette())

        # [KR] 위젯별 QSS 추가 (라이트 - Fluent 스타일 모방)
        app.setStyleSheet("""
            QGroupBox { font-weight: bold; border: 1px solid #ddd; border-radius: 6px; margin-top: 10px; background-color: #fafafa; }
            QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; left: 10px; padding: 0 5px; }
            QPushButton { background-color: #ffffff; border: 1px solid #ccc; border-radius: 4px; padding: 6px 12px; color: #333; }
            QPushButton:hover { background-color: #f0f0f0; border-color: #bbb; }
            QPushButton:pressed { background-color: #e0e0e0; }
            QLineEdit, QComboBox { padding: 6px; border: 1px solid #ccc; border-radius: 4px; background-color: white; }
            QTableWidget { alternate-background-color: #f9f9f9; selection-background-color: #0078d4; selection-color: white; border: 1px solid #ddd; }
            QHeaderView::section { background-color: #f5f5f5; border: none; border-bottom: 1px solid #ccc; padding: 6px; font-weight: bold; color: #555; }
            QListWidget { border: 1px solid #ddd; border-radius: 4px; background-color: white; }
        """)
