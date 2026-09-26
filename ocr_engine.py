import easyocr
from PIL import ImageGrab
import numpy as np

class EasyOCREngine:
    def __init__(self, lang_list=['en']):
        print("[OCR] Инициализация EasyOCR...")
        self.reader = easyocr.Reader(lang_list, gpu=False)
        print("[OCR] Движок успешно запущен на CPU")

    def grab_and_read(self, bbox: tuple) -> str:
        # 1. Захват области экрана
        img = ImageGrab.grab(bbox=bbox)
        
        # 2. Конвертация PIL Image в NumPy массив для EasyOCR
        img_np = np.array(img)
        
        # 3. Распознавание текста
        results = self.reader.readtext(img_np, detail=0)
        
        # 4. Сборка массива строк в единый текст
        text = " ".join(results).strip()
        return text