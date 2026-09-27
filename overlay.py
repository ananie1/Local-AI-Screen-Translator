from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QFont

class SubtitleOverlay(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.drag_position = QPoint()

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self.label = QLabel("Local AI Translator (Зажми ЛКМ, чтобы перетащить)")
        self.label.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        self.label.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                background-color: rgba(15, 15, 15, 230);
                border: 2px solid rgba(255, 255, 255, 60);
                border-radius: 10px;
                padding: 14px 18px;
            }
        """)
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.label)
        self.setLayout(layout)

        self.setFixedWidth(850)
        self.move(300, 700)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def set_text(self, text: str):
        self.label.setText(text)
        self.label.adjustSize()
        self.adjustSize()
        self.updateGeometry()
