# Local AI Screen Translator 2.0

🌐 **Language:** [English](README.md) | [Русский](README_RU.md)

## Overview

Local AI Screen Translator is a lightweight, modular desktop tool that captures any area of your screen, recognizes the text on it (OCR) and translates it into Russian with a language model. The model can run locally (LM Studio, Ollama) or be reached through any OpenAI-compatible API with a key.

It works at the operating-system level, not inside a browser, so it fits games, desktop software, foreign websites, media players and documents alike. The app itself sends nothing anywhere except one request to the LLM server you configure.

## How it works

```text
Select area  →  OCR  →  LLM request  →  Translation overlay
screen_selector  ocr_engine  llm_client      overlay
                  (wired together by main)
```

1. **Capture.** A screenshot of the whole desktop is taken and shown frozen; you drag a rectangle over the text.
2. **OCR.** The cropped image is recognized by [RapidOCR](https://github.com/RapidAI/RapidOCR) (ONNX Runtime, CPU).
3. **Translation.** The text is sent to `/v1/chat/completions` with a system prompt asking for the translation only.
4. **Output.** The result appears in a frameless, always-on-top, semi-transparent window next to the selected area.

OCR and the network request run in a separate thread, so the UI does not freeze.

## Features

- Snipping-Tool-style region selection (multi-monitor and HiDPI aware).
- No external OCR binaries: everything installs through `pip`.
- Any OpenAI-compatible server: LM Studio, Ollama, OpenAI and others.
- Overlay: draggable, copy, collapse, close (`Esc`).
- Reasoning models are supported: `<think>…</think>` blocks are stripped from the answer.
- Connection settings are saved between launches.
- Modular architecture: every module has a single responsibility and can be replaced independently.

## Requirements

- Python 3.10–3.12.
- A running LLM server with a loaded model (for example LM Studio at `http://localhost:1234`) or an API key for a compatible service.
- Windows, macOS or Linux (X11). See [Known limitations](#known-limitations-and-pitfalls).

## Installation

```bash
git clone https://github.com/ananie1/Local-AI-Screen-Translator.git
cd Local-AI-Screen-Translator
python -m venv .venv
# Windows:      .venv\Scripts\activate
# Linux/macOS:  source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

1. Start your LLM server and load a model.
2. In the app window set the **URL**, the **API key** (if needed) and the **model name**.
3. Click **"Выделить область и перевести"** (select area and translate).
4. Drag over the text. `Esc` or right click cancels.
5. The translation appears above the area (below it if there is no room above).

### Connection settings

| Service   | URL                                          | API key      | Model                          |
|-----------|----------------------------------------------|--------------|--------------------------------|
| LM Studio | `http://localhost:1234/v1/chat/completions`  | not required | any (`local-model`)            |
| Ollama    | `http://localhost:11434/v1/chat/completions` | not required | exact name from `ollama list`  |
| OpenAI    | `https://api.openai.com/v1/chat/completions` | required     | e.g. `gpt-4o-mini`             |

### Customization

- **Target language / behaviour:** edit `SYSTEM_PROMPT` in `llm_client.py`.
- **Timeout and temperature:** defaults of `LLMConfig` in `llm_client.py` (120 s and 0.2).
- **OCR engine:** replace the body of `OcrEngine.recognize()` in `ocr_engine.py`; the rest of the app only needs a method that takes a PIL image and returns a string.

## Project structure

| File                 | Purpose                                              |
|----------------------|------------------------------------------------------|
| `main.py`            | Settings GUI, background thread, module wiring       |
| `screen_selector.py` | Region selection and screenshot                      |
| `ocr_engine.py`      | Text recognition                                     |
| `llm_client.py`      | OpenAI-compatible API client                         |
| `overlay.py`         | Transparent translation window                       |

## CPU, GPU and performance

- The bundled OCR runs on the **CPU** only. A GPU is not required and gives no benefit here.
- The LLM is a separate component. Whether it uses CPU or GPU depends only on your server (LM Studio, Ollama) and model settings.
- In practice, translation by the LLM usually takes much longer than OCR, so OCR is rarely the bottleneck.
- Larger selections take longer to recognize and translate. Select only the text you need.

## Known limitations and pitfalls

**OCR**

- The default RapidOCR models recognize Latin and Chinese text, but **not Cyrillic and not Japanese**. The app is aimed at translating *into* Russian from such languages as English.
- Small, low-contrast or stylized text (game fonts, text over busy backgrounds) may be recognized badly. OCR mistakes go straight into the translation.
- Text in several columns can come out interleaved, because lines are ordered top to bottom and then left to right. Select one column at a time.
- Vertical and strongly rotated text is not supported.
- The first OCR call after launch is slower because the model is loaded lazily.

**Screen capture**

- Games in **exclusive fullscreen** and DRM-protected video (some streaming services) may give a black screenshot, and the overlay may not appear on top of them. Use windowed or borderless mode.
- With different DPI scaling on different monitors, the selection edges can be slightly off.
- macOS: grant the app (your terminal or IDE) the **Screen Recording** permission.
- Linux: on Wayland capture through `mss` may not work, use an X11 session.

**LLM**

- The server must be running and a model must be loaded. Otherwise you get a connection error or HTTP 404.
- In Ollama the model name must match `ollama list` exactly.
- Small local models sometimes add comments or refuse, even though the prompt asks for the translation only. Try a larger or instruction-tuned model.
- The first request to a local model can take a long time (loading into memory). The timeout is 120 seconds.
- Very long texts are sent in a single request and can exceed the model's context window.

**Security and privacy**

- With a local LLM, text never leaves your computer. With an external API, **the recognized text is sent to that provider**.
- The API key is stored unencrypted in the application settings (`QSettings`; on Windows this is the registry). Do not use a key with unlimited spending.
- The screenshot is kept in memory only for the duration of one request and is never written to disk.

## Troubleshooting

| Symptom                                   | Likely cause and fix                                                      |
|-------------------------------------------|---------------------------------------------------------------------------|
| "Не удалось подключиться к …"             | Server is not started, wrong port or URL.                                 |
| HTTP 404 / model not found                | Model is not loaded or the name is wrong.                                 |
| HTTP 401 / 403                            | Missing or wrong API key.                                                 |
| "Текст в выделенной области не найден"    | Text too small, low contrast, or unsupported script (Cyrillic, Japanese). |
| Black selection background                | Exclusive fullscreen or protected content, see above.                     |
| Empty or strange translation              | Model is too small or is a reasoning model; try another one.              |

## License

See the `LICENSE` file.
