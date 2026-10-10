"""Прозрачное безрамочное окно поверх всех окон с отображением перевода."""
from __future__ import annotations

from PySide6.QtCore import QPoint, QRect, Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

MIN_WIDTH = 360
MAX_WIDTH = 900
MAX_TEXT_HEIGHT = 480
GAP = 8

STYLE = """
QFrame#card { background-color: rgba(24, 26, 32, 235); border: 1px solid rgba(255,255,255,40);
              border-radius: 12px; }
QLabel#title { color: #8ab4ff; font-size: 11px; font-weight: bold; }
QTextBrowser { background: transparent; border: none; color: #f2f2f2; font-size: 15px; }
QPushButton { background: rgba(255,255,255,18); color: #ddd; border: none; border-radius: 6px;
              min-width: 26px; min-height: 22px; padding: 0 6px; }
QPushButton:hover { background: rgba(255,255,255,50); }
QPushButton#close:hover { background: #d9534f; color: white; }
"""


class TranslationOverlay(QWidget):
    def __init__(self) -> None:
        super().__init__(
            None,
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool,
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setStyleSheet(STYLE)

        self._drag_offset: QPoint | None = None
        self._collapsed = False

        card = QFrame(self)
        card.setObjectName("card")
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(card)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 8, 12, 12)
        layout.setSpacing(6)

        header = QHBoxLayout()
        title = QLabel("Перевод")
        title.setObjectName("title")
        self._copy_btn = QPushButton("Копировать")
        self._fold_btn = QPushButton("Свернуть")
        self._close_btn = QPushButton("✕")
        self._close_btn.setObjectName("close")
        header.addWidget(title)
        header.addStretch(1)
        header.addWidget(self._copy_btn)
        header.addWidget(self._fold_btn)
        header.addWidget(self._close_btn)
        layout.addLayout(header)

        self._text = QTextBrowser()
        self._text.setFrameShape(QFrame.NoFrame)
        self._text.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        layout.addWidget(self._text)

        self._copy_btn.clicked.connect(self._copy)
        self._fold_btn.clicked.connect(self._toggle_fold)
        self._close_btn.clicked.connect(self.hide)

        self._width = MIN_WIDTH
        self._full_height = 120

    # ------------------------------------------------------------------ API
    def show_translation(self, text: str, anchor: QRect | None = None) -> None:
        """Показывает перевод над областью anchor (иначе по центру экрана)."""
        screen = None
        if anchor is not None:
            screen = QGuiApplication.screenAt(anchor.center())
        screen = screen or QGuiApplication.primaryScreen()
        area = screen.availableGeometry()

        width = MIN_WIDTH
        if anchor is not None:
            width = max(MIN_WIDTH, min(anchor.width(), MAX_WIDTH))
        width = min(width, area.width() - 20)

        self._collapsed = False
        self._fold_btn.setText("Свернуть")
        self._text.setVisible(True)
        self._text.setPlainText(text)

        # Высота текста по документу при заданной ширине.
        self._text.setFixedWidth(width - 24)
        doc = self._text.document()
        doc.setTextWidth(width - 24 - 6)
        text_height = min(int(doc.size().height()) + 14, MAX_TEXT_HEIGHT)
        self._text.setFixedHeight(text_height)

        self._width = width
        self.setFixedWidth(width)
        self.adjustSize()
        self._full_height = self.height()

        self._place(area, anchor)
        self.show()
        self.raise_()

    # -------------------------------------------------------------- helpers
    def _place(self, area: QRect, anchor: QRect | None) -> None:
        h = self.height()
        if anchor is None:
            x = area.x() + (area.width() - self._width) // 2
            y = area.y() + (area.height() - h) // 2
        else:
            x = anchor.x()
            y = anchor.y() - h - GAP
            if y < area.y():  # сверху нет места — показываем снизу
                y = anchor.bottom() + GAP
                if y + h > area.bottom():  # и снизу нет — по центру экрана
                    y = area.y() + (area.height() - h) // 2
        x = max(area.x(), min(x, area.right() - self._width))
        y = max(area.y(), min(y, area.bottom() - h))
        self.move(x, y)

    def _copy(self) -> None:
        QApplication.clipboard().setText(self._text.toPlainText())
        self._copy_btn.setText("Скопировано")

    def _toggle_fold(self) -> None:
        self._collapsed = not self._collapsed
        self._text.setVisible(not self._collapsed)
        self._fold_btn.setText("Развернуть" if self._collapsed else "Свернуть")
        self.setFixedHeight(16777215)
        self.adjustSize()
        self.setFixedWidth(self._width)

    # --------------------------------------------------- dragging & hotkeys
    def mousePressEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.LeftButton:
            self._drag_offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event) -> None:  # noqa: N802
        if self._drag_offset is not None and event.buttons() & Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_offset)

    def mouseReleaseEvent(self, _event) -> None:  # noqa: N802
        self._drag_offset = None

    def keyPressEvent(self, event) -> None:  # noqa: N802
        if event.key() == Qt.Key_Escape:
            self.hide()

    def showEvent(self, event) -> None:  # noqa: N802
        self._copy_btn.setText("Копировать")
        super().showEvent(event)
