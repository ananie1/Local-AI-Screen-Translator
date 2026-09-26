import requests

class LLMTranslator:
    def __init__(self, api_url="http://localhost:1234/v1", api_key="lm-studio", model="local-model"):
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key
        self.model = model
        self.history = []
        self.max_history = 5

        self.system_prompt = (
            "Ты — элитный локализатор видеоигр и художественных текстов. "
            "Твоя цель — создавать максимально живой, естественный и глубокий перевод на русский язык.\n\n"
            "СТРОГИЕ ПРАВИЛА ПЕРЕВОДА:\n"
            "1. НИКАКОГО ДОСЛОВНОГО И МАШИННОГО ПЕРЕВОДА. Избегай канцеляризмов и калек с английского.\n"
            "2. АДАПТАЦИЯ МЕТАФОР И ИДИОМ. Переводи под естественные обороты русского языка.\n"
            "3. ЖИВОЙ ИГРОВОЙ СТИЛЬ. Сохраняй контекст, разговорную речь, сленг и атмосферу.\n"
            "4. ФОРМАТ ОТВЕТА. Выводи СТРОГО только итоговый текст перевода. Без пояснений и кавычек."
        )

    def translate(self, text: str) -> str:
        if not text.strip():
            return ""

        messages = [{"role": "system", "content": self.system_prompt}]
        for item in self.history:
            messages.append({"role": "user", "content": item["orig"]})
            messages.append({"role": "assistant", "content": item["trans"]})

        messages.append({"role": "user", "content": f"Переведи на русский:\n{text}"})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.3,
        }

        headers = {"Authorization": f"Bearer {self.api_key}"}

        try:
            response = requests.post(f"{self.api_url}/chat/completions", json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            result = response.json()["choices"][0]["message"]["content"].strip()

            self.history.append({"orig": text, "trans": result})
            if len(self.history) > self.max_history:
                self.history.pop(0)

            return result
        except Exception as e:
            return f"[Ошибка LLM API: {e}]"