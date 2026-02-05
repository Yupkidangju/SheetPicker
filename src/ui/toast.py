from PySide6.QtWidgets import QLabel, QWidget, QVBoxLayout
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QColor, QPalette

class ToastMessage(QWidget):
    """
    [KR] 하단에서 떠오르는 비동기 알림 메시지 (Toast).
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.SubWindow)
        self.setAttribute(Qt.WA_TransparentForMouseEvents) # 클릭 통과
        self.setAttribute(Qt.WA_ShowWithoutActivating)

        # [KR] 스타일 설정
        self.lbl_msg = QLabel(self)
        self.lbl_msg.setStyleSheet("""
            background-color: #333333;
            color: white;
            padding: 10px 20px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: bold;
        """)
        self.lbl_msg.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout()
        layout.addWidget(self.lbl_msg)
        self.setLayout(layout)

        # [KR] 애니메이션 설정
        self.anim = QPropertyAnimation(self, b"windowOpacity")
        self.anim.setDuration(500)
        self.anim.setEasingCurve(QEasingCurve.OutQuad)

        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.fade_out)

        self.hide()

    def show_message(self, message, duration=3000):
        self.lbl_msg.setText(message)
        self.adjustSize()

        # [KR] 위치 조정 (부모 윈도우 하단 중앙)
        parent_rect = self.parent().rect()
        x = (parent_rect.width() - self.width()) // 2
        y = parent_rect.height() - self.height() - 50 # 하단에서 50px 위
        self.move(x, y)

        self.setWindowOpacity(0.0)
        self.show()
        self.raise_()

        # Fade In
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(0.9) # 약간 투명
        self.anim.start()

        # 일정 시간 후 Fade Out
        self.timer.start(duration)

    def fade_out(self):
        self.anim.setStartValue(0.9)
        self.anim.setEndValue(0.0)
        self.anim.finished.connect(self.hide)
        self.anim.start()
