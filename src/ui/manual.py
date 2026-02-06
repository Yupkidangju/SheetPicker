from PySide6.QtWidgets import QDialog, QVBoxLayout, QTextBrowser, QPushButton
from PySide6.QtCore import Qt

class HelpDialog(QDialog):
    """
    [KR] 사용자 매뉴얼 다이얼로그.
    미니멀하고 세련된 디자인의 HTML 콘텐츠를 표시합니다.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Data Scavenger Guide")
        self.resize(700, 600)
        self.setStyleSheet("background-color: #1e1e1e; color: #ffffff;")

        layout = QVBoxLayout()
        self.setLayout(layout)

        # [KR] HTML 콘텐츠 (Minimalistic Dark Theme)
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: 'Segoe UI', sans-serif; padding: 20px; color: #ddd; line-height: 1.6; }
                h1 { color: #4facfe; border-bottom: 2px solid #4facfe; padding-bottom: 10px; font-weight: 300; }
                h2 { color: #00f2fe; margin-top: 30px; font-weight: 400; }
                .card { background-color: #2d2d2d; padding: 15px; border-radius: 8px; margin-bottom: 15px; border-left: 4px solid #4facfe; }
                .key { color: #ffeb3b; font-weight: bold; font-family: monospace; background-color: #444; padding: 2px 6px; border-radius: 4px; }
                .example { color: #aaa; font-style: italic; margin-top: 5px; }
                b { color: #fff; }
            </style>
        </head>
        <body>
            <h1>Data Scavenger Guide</h1>
            <p>Welcome to the ultimate search tool. Simple, fast, and powerful.</p>

            <h2>🚀 Smart Search</h2>
            <div class="card">
                <p><b>AND Search:</b> Use space to find rows containing ALL words.</p>
                <p>Example: <span class="key">Seoul Gangnam</span> <div class="example">Finds rows with both "Seoul" and "Gangnam"</div></p>
            </div>
            <div class="card">
                <p><b>OR Search:</b> Use <span class="key">|</span> to find rows containing ANY word.</p>
                <p>Example: <span class="key">Apple|Banana</span> <div class="example">Finds rows with "Apple" or "Banana"</div></p>
            </div>
            <div class="card">
                <p><b>NOT Search:</b> Use <span class="key">-</span> to exclude words.</p>
                <p>Example: <span class="key">Sales -2023</span> <div class="example">Finds "Sales" but excludes rows with "2023"</div></p>
            </div>
            <div class="card">
                <p><b>Exact Phrase:</b> Use quotes <span class="key">""</span>.</p>
                <p>Example: <span class="key">"Order ID"</span> <div class="example">Finds exact phrase "Order ID" (with space)</div></p>
            </div>

            <h2>⚡ Power Features</h2>
            <ul>
                <li><b>Targeting:</b> Limit search to specific columns (e.g., <span class="key">Email, ID</span>).</li>
                <li><b>Regex:</b> Check the box to use full Regular Expressions (e.g., <span class="key">\d{3}-\d{4}</span>).</li>
                <li><b>Favorites:</b> Save your frequently used folders for one-click access.</li>
            </ul>
        </body>
        </html>
        """

        self.browser = QTextBrowser()
        self.browser.setHtml(html_content)
        self.browser.setStyleSheet("border: none; font-size: 14px;")
        layout.addWidget(self.browser)

        btn_close = QPushButton("Close Guide")
        btn_close.clicked.connect(self.close)
        btn_close.setStyleSheet("""
            QPushButton {
                background-color: #4facfe;
                color: #000;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover { background-color: #00f2fe; }
        """)
        layout.addWidget(btn_close)
