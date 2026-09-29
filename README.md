# Local AI Screen Translator EN

🌐 **Language:** [English](README.md) | [Русский](README_RU.md)

## Overview

Local AI Screen Translator is a lightweight, modular desktop utility designed to capture, recognize, and translate text from any region of your screen in real time. Built with privacy and offline performance in mind, the application processes text locally using Optical Character Recognition (OCR) and translates it via a locally hosted Large Language Model (LLM) or compatible API keys.

Unlike traditional translators restricted to web browsers, this tool operates globally across the operating system interface. It is perfectly suited for video games, desktop software, foreign websites, media players, and documents, allowing you to translate text seamlessly without sending your data to external cloud servers.

## How It Works

* **Screen Capture:** The user selects a specific area on the screen using a custom interactive overlay.
* **Text Recognition (OCR):** The application extracts raw text from the captured image using the offline EasyOCR engine.
* **Neural Translation:** The extracted text is transmitted via a local API to a running LLM instance (such as LM Studio), which translates the text contextually into the target language.
* **Display:** The translated result is presented cleanly to the user.

## How CPU, GPU, and LLM Are Used

The software consists of several independent components, and they do not all use the GPU.

The translation process works as follows:

1. **Screen Capture** — the application captures the selected area of the screen.
2. **OCR** — EasyOCR analyzes the captured image and extracts the text.

   * If a CUDA-compatible NVIDIA GPU is available, EasyOCR uses the GPU for OCR processing.
   * If CUDA is unavailable, EasyOCR automatically falls back to the CPU.
3. **LLM Translation** — the recognized text is sent to a locally running LLM server, such as LM Studio, or to a compatible external API.
4. **Display** — the translated text is displayed in the application overlay.

The GPU acceleration described above applies specifically to **OCR processing**. It does not mean that the entire application runs on the GPU.

The LLM is a separate component. If LM Studio is used, the way the LLM itself uses the CPU or GPU is determined by LM Studio and its model configuration, independently of the OCR engine.

In simplified form:

```text
Screen
   ↓
Screen Capture
   ↓
EasyOCR
   ├── NVIDIA GPU + CUDA
   └── CPU (fallback)
   ↓
Recognized Text
   ↓
LM Studio / Compatible API
   ↓
LLM Translation
   ↓
Translated Text
   ↓
Overlay
```

The application therefore does not require a dedicated GPU. A GPU is only an optional acceleration method for the OCR stage.

## Key Features

* **Full Privacy:** When used with a local LLM, all processing remains on your hardware. No telemetry or third-party cloud tracking is included.
* **Universal Compatibility:** Works over any full-screen or windowed application, web page, or document interface.
* **Modular Architecture:** Clean separation of concerns between the graphical interface, screen selector, OCR processing, and LLM communication clients.
* **System Tray Integration:** Runs discreetly in the background with quick access controls.

## System Requirements

* Python 3.10 or higher.
* A running local LLM server instance (such as LM Studio active on `http://localhost:1234`) or a valid API endpoint key for compatible services.
* **GPU acceleration (optional):** NVIDIA GPU with a CUDA-compatible PyTorch installation. The application automatically uses the GPU when CUDA is available and falls back to CPU otherwise.

### GPU Acceleration

GPU acceleration is optional. The application can run entirely on the CPU.

* **NVIDIA GPUs:** For CUDA acceleration, install the appropriate CUDA-enabled PyTorch version for your GPU using the official PyTorch installation guide:
  https://pytorch.org/get-started/locally/
* **AMD GPUs:** CUDA is not supported. The application will automatically use the CPU.
* **Intel Arc GPUs:** CUDA is not supported. The application will automatically use the CPU.
* **No dedicated GPU:** The application will automatically use the CPU.

For NVIDIA GPUs, when configuring PyTorch, select:

* **OS:** Windows
* **Package:** Pip
* **Language:** Python
* **Compute Platform:** The CUDA version appropriate for your GPU

The application automatically detects CUDA at startup. If CUDA is available, EasyOCR uses the NVIDIA GPU; otherwise, it falls back to the CPU.

## Installation

Clone the repository:

```bash
git clone https://github.com/ananie1/ananie1-Local-AI-Screen-Translator.git
cd ananie1-Local-AI-Screen-Translator
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Configuration and Usage

### Running the Application

Execute the main entry point script:

```bash
python main.py
```

### Changing Hotkeys

Global keyboard shortcuts are handled via the `keyboard` library. To modify the shortcut bindings, open the primary event handler file and locate the hotkey registration lines. Replace the default key string with your preferred key combination.

### Changing Languages

* **OCR Language:** The recognition language can be changed in `ocr_engine.py` by modifying the `lang_list` parameter. Multiple languages can be specified at the same time, for example `['en', 'ru', 'de']`.
* **Translation Language:** The target language for translation is controlled through the system prompt in `llm_client.py`.

## Project Structure

* `main.py` - Application entry point, system tray logic, and core event loop.
* `overlay.py` - Semi-transparent graphical interface for screen region selection.
* `ocr_engine.py` - Text recognition wrapper utilizing EasyOCR.
* `llm_client.py` - API communication layer interfacing with the local LLM server.
* `screen_selector.py` - Screen coordinate capture utility.

## License

Distributed under the MIT License.

---
