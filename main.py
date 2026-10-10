"""Главный модуль: GUI настроек и связывание цепочки
Захват области -> OCR -> LLM -> Оверлей."""
from __future__ import annotations

import sys

from PIL import Image
from PySide6.QtCore import QRect, QSettings, Qt, QThread, QTimer, Signal
from PySide6.QtWidgets import (
    QApplication,
    QFormLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from llm_client import DEFAULT_URL, LLMClient, LLMConfig
from ocr_engine import OcrEngine
from overlay import TranslationOverlay
from screen_selector import ScreenSelector, Selection


class PipelineThread(QThread):
    """Фоновая цепочка OCR -> LLM. GUI-поток при этом не блокируется."""

    status = Signal(str)
    recognized = Signal(str)
    translated = Signal(str)
    failed = Signal(str)

    def __init__(self, ocr: OcrEngine, llm: LLMClient, image: Image.Image, parent=None) -> None:
        super().__init__(parent)
        self._ocr = ocr
        self._llm = llm
        self._image = image

    def run(self) -> None:
        try:
            self.status.emit("Распознавание текста…")
            text = self._ocr.recognize(self._image)
            if not text.strip():
                self.failed.emit("Текст в выделенной области не найден.")
                return
            self.recognized.emit(text)

            self.status.emit("Перевод через LLM…")
            result = self._llm.translate(text)
            self.translated.emit(result)
        except Exception as exc:  # noqa: BLE001
            self.failed.emit(str(exc))


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Умный экранный переводчик")
        self.setMinimumWidth(480)

        self._settings = QSettings("ScreenTranslator", "ScreenTranslator")
        self._ocr = OcrEngine()
        self._selector = ScreenSelector()
        self._overlay = TranslationOverlay()
        self._thread: PipelineThread | None = None
        self._anchor: QRect | None = None

        self._build_ui()
        self._load_settings()

        self._selector.selected.connect(self._on_selected)
        self._selector.cancelled.connect(self._on_cancelled)

    # ------------------------------------------------------------------ UI
    def _build_ui(self) -> None:
        self._url = QLineEdit()
        self._url.setPlaceholderText(DEFAULT_URL)
        self._key = QLineEdit()
        self._key.setEchoMode(QLineEdit.Password)
        self._key.setPlaceholderText("Оставьте пустым для локальной модели")
        self._model = QLineEdit()
        self._model.setPlaceholderText("например, local-model или llama3")

        form = QFormLayout()
        form.addRow("URL сервера:", self._url)
        form.addRow("API-ключ:", self._key)
        form.addRow("Модель:", self._model)
        group = QGroupBox("Подключение к LLM")
        group.setLayout(form)

        self._button = QPushButton("Выделить область и перевести")
        self._button.setMinimumHeight(40)
        self._button.clicked.connect(self._start)

        self._status = QLabel("Готово к работе.")
        self._status.setWordWrap(True)

        self._source = QPlainTextEdit()
        self._source.setReadOnly(True)
        self._source.setPlaceholderText("Здесь появится распознанный текст…")
        self._source.setMaximumHeight(110)

        layout = QVBoxLayout()
        layout.addWidget(group)
        layout.addWidget(self._button)
        layout.addWidget(self._status)
        layout.addWidget(QLabel("Распознанный текст:"))
        layout.addWidget(self._source)
        central = QWidget()
        central.setLayout(layout)
        self.setCentralWidget(central)

    def _load_settings(self) -> None:
        self._url.setText(self._settings.value("url", DEFAULT_URL))
        self._key.setText(self._settings.value("api_key", ""))
        self._model.setText(self._settings.value("model", "local-model"))

    def _save_settings(self) -> None:
        self._settings.setValue("url", self._url.text().strip())
        self._settings.setValue("api_key", self._key.text().strip())
        self._settings.setValue("model", self._model.text().strip())

    def _config(self) -> LLMConfig:
        return LLMConfig(
            url=self._url.text().strip() or DEFAULT_URL,
            api_key=self._key.text().strip(),
            model=self._model.text().strip() or "local-model",
        )

    # ------------------------------------------------------------ pipeline
    def _start(self) -> None:
        if self._thread is not None and self._thread.isRunning():
            return
        self._save_settings()
        self._overlay.hide()
        self._button.setEnabled(False)
        self.hide()  # убираем главное окно, чтобы оно не попало в кадр
        QTimer.singleShot(250, self._selector.start)

    def _on_cancelled(self) -> None:
        self._button.setEnabled(True)
        self._status.setText("Выделение отменено.")
        self._restore_window()

    def _on_selected(self, selection: Selection) -> None:
        self._anchor = selection.rect
        self._restore_window()
        self._source.clear()

        thread = PipelineThread(self._ocr, LLMClient(self._config()), selection.image, self)
        thread.status.connect(self._status.setText)
        thread.recognized.connect(self._source.setPlainText)
        thread.translated.connect(self._on_translated)
        thread.failed.connect(self._on_failed)
        thread.finished.connect(self._on_thread_finished)
        self._thread = thread
        thread.start()

    def _on_translated(self, text: str) -> None:
        self._status.setText("Готово.")
        self._overlay.show_translation(text, self._anchor)

    def _on_failed(self, message: str) -> None:
        self._status.setText(f"Ошибка: {message}")
        QMessageBox.warning(self, "Ошибка", message)

    def _on_thread_finished(self) -> None:
        self._button.setEnabled(True)

    def _restore_window(self) -> None:
        self.show()
        self.raise_()
        self.activateWindow()

    def closeEvent(self, event) -> None:  # noqa: N802
        self._save_settings()
        self._overlay.hide()
        if self._thread is not None and self._thread.isRunning():
            self._thread.wait(3000)
        event.accept()
        QApplication.quit()


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("ScreenTranslator")
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
