"""Клиент OpenAI-совместимого API (LM Studio, Ollama, OpenAI и др.)."""
from __future__ import annotations

import re
from dataclasses import dataclass

import requests

SYSTEM_PROMPT = (
    "Переведи следующий текст на русский язык, сохраняя смысл. "
    "Выведи ТОЛЬКО готовый перевод без лишних вводных фраз"
)

DEFAULT_URL = "http://localhost:1234/v1/chat/completions"


class LLMError(RuntimeError):
    """Ошибка обращения к LLM."""


@dataclass
class LLMConfig:
    url: str = DEFAULT_URL
    api_key: str = ""
    model: str = "local-model"
    timeout: float = 120.0
    temperature: float = 0.2


class LLMClient:
    def __init__(self, config: LLMConfig) -> None:
        self.config = config

    def translate(self, text: str) -> str:
        cfg = self.config
        if not cfg.url.strip():
            raise LLMError("Не указан URL LLM-сервера.")
        if not text.strip():
            raise LLMError("Нет текста для перевода.")

        headers = {"Content-Type": "application/json"}
        if cfg.api_key.strip():
            headers["Authorization"] = f"Bearer {cfg.api_key.strip()}"

        payload = {
            "model": cfg.model.strip() or "local-model",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text},
            ],
            "temperature": cfg.temperature,
            "stream": False,
        }

        try:
            response = requests.post(
                cfg.url.strip(), headers=headers, json=payload, timeout=cfg.timeout
            )
        except requests.ConnectionError as exc:
            raise LLMError(f"Не удалось подключиться к {cfg.url}. Сервер запущен?") from exc
        except requests.Timeout as exc:
            raise LLMError("Превышено время ожидания ответа от LLM.") from exc
        except requests.RequestException as exc:
            raise LLMError(f"Сетевая ошибка: {exc}") from exc

        if response.status_code != 200:
            raise LLMError(f"LLM вернула HTTP {response.status_code}: {response.text[:300]}")

        try:
            content = response.json()["choices"][0]["message"]["content"]
        except (ValueError, KeyError, IndexError, TypeError) as exc:
            raise LLMError(f"Неожиданный формат ответа: {response.text[:300]}") from exc

        # Убираем «размышления» моделей-рассуждателей.
        content = re.sub(r"<think>.*?</think>", "", content or "", flags=re.DOTALL).strip()
        if not content:
            raise LLMError("LLM вернула пустой ответ.")
        return content
