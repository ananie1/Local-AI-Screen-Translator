import sys
import keyboard
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, 
    QPushButton, QLineEdit, QLabel, QHBoxLayout, QGroupBox,
    QSystemTrayIcon, QMenu
)
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QThread
from PyQt6.QtGui import QIcon, QAction
from overlay import SubtitleOverlay
from ocr_engine import EasyOCREngine
from llm_client import LLMTranslator
from screen_selector import ScreenSelector

class HotkeySignaler(QObject):
    select_triggered = pyqtSignal()
    retranslate_triggered = pyqtSignal()

# A thread for background OCR loading to prevent the window from freezing
class OCRInitWorker(QThread):
    loaded = pyqtSignal(object)

    def __init__(self, lang_list):
        super().__init__()
        self.lang_list = lang_list

    def run(self):
        ocr = EasyOCREngine(self.lang_list)
        self.loaded.emit(ocr)


# Runs OCR and LLM translation outside the GUI thread.
class TranslationWorker(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, ocr, llm, bbox, api_url):
        super().__init__()
        self.ocr = ocr
        self.llm = llm
        self.bbox = bbox
        self.api_url = api_url

    def run(self):
        try:
            self.llm.api_url = self.api_url
            raw_text = self.ocr.grab_and_read(self.bbox)
            if not raw_text.strip():
                self.finished.emit("[No text found]")
                return

            translated = self.llm.translate(raw_text)
            self.finished.emit(translated)
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Local AI Screen Translator")
        self.resize(440, 320)

        self.ocr = None  # While it’s loading in the background
        self.llm = LLMTranslator(api_url="http://localhost:1234/v1")
        
        self.overlay = SubtitleOverlay()
        self.overlay.show()

        self.selector = ScreenSelector()
        self.selector.area_selected.connect(self.on_area_selected)

        self.current_bbox = None
        self.worker = None

        self.signaler = HotkeySignaler()
        self.signaler.select_triggered.connect(self.start_selection)
        self.signaler.retranslate_triggered.connect(self.process_translation)

        self.init_ui()
        self.setup_tray()
        self.setup_hotkeys()

        # We start the OCR loading in the background thread
        self.status_label.setText("Loading OCR in the background...")
        self.init_worker = OCRInitWorker(['en'])
        self.init_worker.loaded.connect(self.on_ocr_loaded)
        self.init_worker.start()

    def on_ocr_loaded(self, ocr_engine):
        self.ocr = ocr_engine
        self.status_label.setText("Ready. Press Alt+T")

    def init_ui(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #121212;
                color: #E0E0E0;
                font-family: 'Segoe UI', sans-serif;
            }
            QGroupBox {
                border: 1px solid #2A2A2A;
                border-radius: 8px;
                margin-top: 10px;
                font-weight: bold;
                color: #888888;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QLineEdit {
                background-color: #1E1E1E;
                border: 1px solid #333333;
                border-radius: 6px;
                padding: 8px 12px;
                color: #FFFFFF;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 1px solid #007ACC;
            }
            QPushButton {
                background-color: #252526;
                border: 1px solid #3E3E42;
                border-radius: 6px;
                padding: 10px 16px;
                color: #FFFFFF;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #2D2D30;
                border-color: #007ACC;
            }
            QPushButton#primary_btn {
                background-color: #0066B8;
                border: none;
            }
            QPushButton#primary_btn:hover {
                background-color: #0078D4;
            }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(14)
        layout.setContentsMargins(20, 20, 20, 20)

        api_group = QGroupBox(" AI CONNECTION ")
        api_layout = QVBoxLayout()
        self.url_input = QLineEdit("http://localhost:1234/v1")
        api_layout.addWidget(self.url_input)
        api_group.setLayout(api_layout)
        layout.addWidget(api_group)

        controls_group = QGroupBox(" CONTROLS (HOTKEYS) ")
        controls_layout = QVBoxLayout()
        controls_layout.setSpacing(10)

        select_row = QHBoxLayout()
        self.btn_select = QPushButton("✂ Select area")
        self.btn_select.setObjectName("primary_btn")
        self.btn_select.clicked.connect(self.start_selection)
        hk_select_label = QLabel("Alt + T")
        hk_select_label.setStyleSheet("color: #007ACC; font-weight: bold; padding-left: 5px;")
        select_row.addWidget(self.btn_select, stretch=2)
        select_row.addWidget(hk_select_label, stretch=1)
        controls_layout.addLayout(select_row)

        retrans_row = QHBoxLayout()
        self.btn_retranslate = QPushButton("🔄 Translate again")
        self.btn_retranslate.clicked.connect(self.process_translation)
        hk_retrans_label = QLabel("Alt + R")
        hk_retrans_label.setStyleSheet("color: #007ACC; font-weight: bold; padding-left: 5px;")
        retrans_row.addWidget(self.btn_retranslate, stretch=2)
        retrans_row.addWidget(hk_retrans_label, stretch=1)
        controls_layout.addLayout(retrans_row)

        controls_group.setLayout(controls_layout)
        layout.addWidget(controls_group)

        self.status_label = QLabel("Initializing...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #777777; font-size: 11px; margin-top: 5px;")
        layout.addWidget(self.status_label)

        self.setLayout(layout)

    def setup_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        
        # Use a temporary standard Qt icon for the system tray
        standard_icon = self.style().standardIcon(self.style().StandardPixmap.SP_ComputerIcon)
        self.tray_icon.setIcon(standard_icon)
        self.setWindowIcon(standard_icon)

        tray_menu = QMenu()
        show_action = QAction("Open window", self)
        show_action.triggered.connect(self.show_window)
        
        quit_action = QAction("Exit application", self)
        quit_action.triggered.connect(self.force_quit)

        tray_menu.addAction(show_action)
        tray_menu.addSeparator()
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.on_tray_icon_activated)
        self.tray_icon.show()

    def on_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            if self.isVisible():
                self.hide()
            else:
                self.show_window()

    def show_window(self):
        self.show()
        self.activateWindow()

    def force_quit(self):
        keyboard.unhook_all()
        QApplication.quit()

    def setup_hotkeys(self):
        try:
            keyboard.add_hotkey('alt+t', lambda: self.signaler.select_triggered.emit())
            keyboard.add_hotkey('alt+r', lambda: self.signaler.retranslate_triggered.emit())
        except Exception as e:
            self.status_label.setText(f"Hotkey error: {e}")

    def start_selection(self):
        if self.ocr is None:
            self.status_label.setText("Please wait, OCR is still loading in the background...")
            return
        self.selector.show()

    def on_area_selected(self, bbox: tuple):
        x, y, w, h = bbox
        # Convert the width/height to final coordinates (right and bottom edges)
        self.current_bbox = (x, y, x + w, y + h)
        self.process_translation()

    def process_translation(self):
        if self.ocr is None:
            self.status_label.setText("Please wait, OCR is still loading in the background...")
            return

        if not self.current_bbox:
            self.status_label.setText("Select an area first (Alt+T)!")
            return

        # Prevent multiple translation workers from running at the same time.
        if self.worker is not None and self.worker.isRunning():
            return

        self.overlay.set_text("Translating with AI...")
        self.status_label.setText("Status: Sending request to AI...")

        api_url = self.url_input.text().rstrip('/')
        self.worker = TranslationWorker(self.ocr, self.llm, self.current_bbox, api_url)
        self.worker.finished.connect(self.on_translation_finished)
        self.worker.error.connect(self.on_translation_error)
        self.worker.start()

    def on_translation_finished(self, text: str):
        self.overlay.set_text(text)
        self.status_label.setText("Status: Translation updated")

    def on_translation_error(self, err_msg: str):
        print(f"CAUGHT ERROR: {err_msg}")
        self.overlay.set_text("[Translation error]")
        self.status_label.setText(f"Error: {err_msg}")

    def closeEvent(self, event):
        if self.tray_icon.isVisible():
            self.hide()
            event.ignore()
        else:
            event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())