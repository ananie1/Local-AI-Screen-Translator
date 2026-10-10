"""Модуль распознавания текста на базе RapidOCR (ONNX, только CPU)."""
from __future__ import annotations

import threading

import numpy as np
from PIL import Image


class OcrError(RuntimeError):
    """Ошибка инициализации или работы OCR."""


class OcrEngine:
    """Ленивая обёртка над RapidOCR. Потокобезопасна."""

    def __init__(self) -> None:
        self._engine = None
        self._lock = threading.Lock()

    def _get_engine(self):
        if self._engine is None:
            try:
                from rapidocr_onnxruntime import RapidOCR
            except ImportError as exc:  # pragma: no cover
                raise OcrError(
                    "Не установлен rapidocr-onnxruntime. "
                    "Выполните: pip install rapidocr-onnxruntime"
                ) from exc
            self._engine = RapidOCR()
        return self._engine

    @staticmethod
    def _prepare(image: Image.Image) -> np.ndarray:
        img = image.convert("RGB")
        # Мелкий текст распознаётся заметно лучше после увеличения.
        if min(img.size) < 120:
            img = img.resize((img.width * 2, img.height * 2), Image.LANCZOS)
        return np.ascontiguousarray(np.array(img)[:, :, ::-1])  # RGB -> BGR

    def recognize(self, image: Image.Image) -> str:
        """Возвращает распознанный текст (строки разделены переводом строки)."""
        array = self._prepare(image)
        try:
            with self._lock:
                result, _ = self._get_engine()(array)
        except OcrError:
            raise
        except Exception as exc:
            raise OcrError(f"Ошибка распознавания: {exc}") from exc

        if not result:
            return ""

        # item: [box(4 точки), text, score]. Сортируем по строкам сверху вниз, слева направо.
        def key(item):
            box = item[0]
            top = min(p[1] for p in box)
            left = min(p[0] for p in box)
            return (round(top / 12), left)

        lines = [item[1].strip() for item in sorted(result, key=key) if item[1].strip()]
        return "\n".join(lines)
