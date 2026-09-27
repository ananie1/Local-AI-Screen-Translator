import easyocr
from PIL import ImageGrab
import numpy as np
import torch


class EasyOCREngine:
    def __init__(self, lang_list=None):
        if lang_list is None:
            lang_list = ['en']

        print("[OCR] Initializing EasyOCR...")

        gpu_available = torch.cuda.is_available()

        self.reader = easyocr.Reader(
            lang_list,
            gpu=gpu_available
        )

        if gpu_available:
            print(f"[OCR] Engine successfully started on GPU: {torch.cuda.get_device_name(0)}")
        else:
            print("[OCR] CUDA is unavailable. Engine started on CPU")

    def grab_and_read(self, bbox: tuple) -> str:
        # Capture the selected screen region.
        img = ImageGrab.grab(bbox=bbox)

        # Convert the PIL image to a NumPy array required by EasyOCR.
        img_np = np.array(img)

        # Run OCR and return detected text without bounding box data.
        results = self.reader.readtext(img_np, detail=0)

        text = " ".join(results).strip()
        return text