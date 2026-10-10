"""Модуль выделения области экрана (аналог «Ножниц»)."""
from __future__ import annotations

from dataclasses import dataclass

import mss
from PIL import Image
from PySide6.QtCore import QPoint, QRect, QRectF, Qt, Signal
from PySide6.QtGui import QColor, QCursor, QImage, QPainter, QPen, QPixmap
from PySide6.QtWidgets import QApplication, QWidget

MIN_SIDE = 10  # минимальный размер области в пикселях


@dataclass(frozen=True)
class Selection:
    """Результат выделения: логические координаты на экране + скриншот области."""

    x: int
    y: int
    width: int
    height: int
    image: Image.Image

    @property
    def rect(self) -> QRect:
        return QRect(self.x, self.y, self.width, self.height)


class ScreenSelector(QWidget):
    """Полноэкранное (на весь виртуальный рабочий стол) окно выделения мышью."""

    selected = Signal(object)  # Selection
    cancelled = Signal()

    def __init__(self) -> None:
        super().__init__(
            None,
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool,
        )
        self.setCursor(QCursor(Qt.CrossCursor))
        self.setAttribute(Qt.WA_DeleteOnClose, False)
        self.setMouseTracking(True)

        self._image: Image.Image | None = None
        self._pixmap: QPixmap | None = None
        self._origin = QPoint()
        self._current = QPoint()
        self._dragging = False
        self._geo = QRect()
        self._sx = 1.0
        self._sy = 1.0

    # ------------------------------------------------------------------ API
    def start(self) -> None:
        """Делает снимок всего рабочего стола и показывает окно выделения."""
        screens = QApplication.screens()
        geo = screens[0].geometry()
        for screen in screens[1:]:
            geo = geo.united(screen.geometry())
        self._geo = geo

        with mss.mss() as sct:
            shot = sct.grab(sct.monitors[0])  # весь виртуальный рабочий стол
            self._image = Image.frombytes("RGB", shot.size, shot.bgra, "raw", "BGRX")
            qimg = QImage(shot.bgra, shot.width, shot.height, QImage.Format_RGB32).copy()

        self._pixmap = QPixmap.fromImage(qimg)
        self._sx = self._image.width / geo.width()
        self._sy = self._image.height / geo.height()

        self._dragging = False
        self._origin = self._current = QPoint()
        self.setGeometry(geo)
        self.show()
        self.raise_()
        self.activateWindow()
        self.setFocus()

    # --------------------------------------------------------------- events
    def _selection_rect(self) -> QRect:
        return QRect(self._origin, self._current).normalized()

    def paintEvent(self, _event) -> None:  # noqa: N802
        if self._pixmap is None:
            return
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), self._pixmap)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 110))

        if self._dragging:
            sel = self._selection_rect()
            source = QRectF(
                sel.x() * self._sx,
                sel.y() * self._sy,
                sel.width() * self._sx,
                sel.height() * self._sy,
            )
            painter.drawPixmap(QRectF(sel), self._pixmap, source)
            painter.setPen(QPen(QColor(0, 160, 255), 2))
            painter.drawRect(sel)
            label = f"{sel.width()} × {sel.height()}"
            painter.setPen(QColor(255, 255, 255))
            painter.fillRect(sel.x(), max(0, sel.y() - 22), 90, 20, QColor(0, 0, 0, 180))
            painter.drawText(sel.x() + 6, max(14, sel.y() - 7), label)
        painter.end()

    def mousePressEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.LeftButton:
            self._origin = self._current = event.position().toPoint()
            self._dragging = True
            self.update()
        elif event.button() == Qt.RightButton:
            self._cancel()

    def mouseMoveEvent(self, event) -> None:  # noqa: N802
        if self._dragging:
            self._current = event.position().toPoint()
            self.update()

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802
        if event.button() != Qt.LeftButton or not self._dragging:
            return
        self._dragging = False
        self._current = event.position().toPoint()
        sel = self._selection_rect().intersected(self.rect())
        if sel.width() < MIN_SIDE or sel.height() < MIN_SIDE or self._image is None:
            self._cancel()
            return

        box = (
            round(sel.left() * self._sx),
            round(sel.top() * self._sy),
            round((sel.left() + sel.width()) * self._sx),
            round((sel.top() + sel.height()) * self._sy),
        )
        cropped = self._image.crop(box)
        result = Selection(
            x=self._geo.x() + sel.x(),
            y=self._geo.y() + sel.y(),
            width=sel.width(),
            height=sel.height(),
            image=cropped,
        )
        self._release()
        self.selected.emit(result)

    def keyPressEvent(self, event) -> None:  # noqa: N802
        if event.key() == Qt.Key_Escape:
            self._cancel()

    # -------------------------------------------------------------- helpers
    def _release(self) -> None:
        self.hide()
        self._pixmap = None
        self._image = None

    def _cancel(self) -> None:
        self._release()
        self.cancelled.emit()
