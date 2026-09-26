# Local AI Screen Translator EN

## Overview

Local AI Screen Translator is a lightweight, modular desktop utility designed to capture, recognize, and translate text from any region of your screen in real time. Built with privacy and offline performance in mind, the application processes text locally using Optical Character Recognition (OCR) and translates it via a locally hosted Large Language Model (LLM) or compatible API keys.

Unlike traditional translators restricted to web browsers, this tool operates globally across the operating system interface. It is perfectly suited for video games, desktop software, foreign websites, media players, and documents, allowing you to translate text seamlessly without sending your data to external cloud servers.

## How It Works

* **Screen Capture:** The user selects a specific area on the screen using a custom interactive overlay.
* **Text Recognition (OCR):** The application extracts raw text from the captured image using the offline EasyOCR engine.
* **Neural Translation:** The extracted text is transmitted via a local API to a running LLM instance (such as LM Studio), which translates the text contextually into the target language.
* **Display:** The translated result is presented cleanly to the user.

## Key Features

* **Full Privacy:** Operates entirely offline on your hardware. No telemetry, no third-party cloud tracking.
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

* **OCR Language:** The recognition language can be adjusted in the OCR engine initialization module by modifying parameters.
* **Translation Language:** The target language for translation is controlled directly through the system prompt configuration sent to the local LLM client.

## Project Structure

* `main.py` - Application entry point, system tray logic, and core event loop.
* `overlay.py` - Semi-transparent graphical interface for screen region selection.
* `ocr_engine.py` - Text recognition wrapper utilizing EasyOCR.
* `llm_client.py` - API communication layer interfacing with the local LLM server.
* `screen_selector.py` - Screen coordinate capture utility.

## License

Distributed under the MIT License.

---

# Local AI Screen Translator RU

## Обзор

Local AI Screen Translator — это легковесная модульная утилита для захвата, распознавания и перевода текста из любой области экрана в режиме реального времени. Приложение разработано с упором на конфиденциальность и автономность: обработка текста выполняется локально с помощью оптического распознавания символов (OCR), а перевод обеспечивается локальной языковой моделью (LLM) или с использованием внешних API-ключей.

В отличие от классических переводчиков, привязанных к браузерам, этот инструмент работает на уровне всей операционной системы. Он отлично подходит как для видеоигр, так и для любых других задач (десктопный софт, зарубежные сайты, медиаплееры и документы), позволяя мгновенно переводить текст без отправки данных на сторонние облачные сервера.

## Принцип работы

* **Захват экрана:** Пользователь выделяет нужную область на экране с помощью интерактивного оверлея.

* **Распознавание текста (OCR):** Модуль EasyOCR производит автономное извлечение текста из полученного графического фрагмента.

* **Нейросетевой перевод:** Извлеченный текст отправляется через локальный API на запущенный сервер языковой модели (например, LM Studio), которая выполняет точный контекстный перевод.

* **Вывод результата:** Готовый перевод отображается в интерфейсе приложения.

## Ключевые особенности

* **Полная конфиденциальность:** Работает полностью офлайн на вашем оборудовании без сторонней телеметрии.

* **Универсальность применения:** Подходит для работы с любыми окнами, приложениями, сайтами и медиаконтентом.

* **Модульная архитектура:** Четкое разделение компонентов на интерфейс, селектор экрана, OCR-движок и клиент взаимодействия с LLM.

* **Системный трей:** Фоновый режим работы с быстрым доступом к управлению через трей Windows.

## Системные требования

* Python версии 3.10 или выше.
* Запущенный локальный сервер языковой модели (например, LM Studio на `http://localhost:1234`) либо действующий API-ключ для работы с совместимыми сервисами.
* **Ускорение на GPU (опционально):** видеокарта NVIDIA с совместимой CUDA-версией PyTorch. Приложение автоматически использует GPU при доступности CUDA и переключается на CPU в противном случае.

### Ускорение на GPU

Использование GPU не является обязательным. Программа может полностью работать на CPU.

* **Видеокарты NVIDIA:** Для ускорения через CUDA установите подходящую CUDA-версию PyTorch в соответствии с вашей видеокартой, используя официальную инструкцию PyTorch:
  https://pytorch.org/get-started/locally/
* **Видеокарты AMD:** CUDA не поддерживается. Программа автоматически использует CPU.
* **Видеокарты Intel Arc:** CUDA не поддерживается. Программа автоматически использует CPU.
* **Без дискретной видеокарты:** Программа автоматически использует CPU.

Для видеокарт NVIDIA при настройке PyTorch выберите:

* **OS:** Windows
* **Package:** Pip
* **Language:** Python
* **Compute Platform:** подходящую CUDA-версию для вашей видеокарты

Программа автоматически определяет наличие CUDA при запуске. Если CUDA доступна, EasyOCR использует видеокарту NVIDIA; в противном случае используется CPU.

## Установка

Клонируйте репозиторий:

```bash
git clone https://github.com/ananie1/ananie1-Local-AI-Screen-Translator.git
cd ananie1-Local-AI-Screen-Translator
```

Установите необходимые зависимости:

```bash
pip install -r requirements.txt
```

## Настройка и использование

### Запуск программы

Выполните запуск главного управляющего файла:

```bash
python main.py
```

### Настройка горячих клавиш

Управление глобальными комбинациями клавиш реализовано через библиотеку `keyboard`. Чтобы изменить используемые сочетания, откройте основной файл обработки событий и найдите строки регистрации хоткеев. Замените стандартные значения на желаемые комбинации клавиш.

### Настройка языков

* **Язык распознавания (OCR):** Настраивается в конфигурационном файле инициализации OCR-модуля путем изменения языковых параметров.

* **Язык перевода:** Целевой язык перевода задается через системный промпт (инструкцию) в модуле клиента LLM.

## Структура проекта

* `main.py` — точка входа, логика системного трея и основной цикл приложения.

* `overlay.py` — полупрозрачный графический интерфейс для выделения области экрана.

* `ocr_engine.py` — модуль распознавания текста на базе EasyOCR.

* `llm_client.py` — клиент для взаимодействия с локальным сервером LLM по API.

* `screen_selector.py` — утилита захвата координат экрана.

## Лицензия

Проект распространяется под лицензией MIT.
