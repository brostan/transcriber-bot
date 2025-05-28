# Audio Transcriber Bot

Telegram бот для транскрибации аудио в текст с использованием OpenAI Whisper API.

## Функциональность

- Прием MP3 файлов через Telegram
- Транскрибация аудио в текст с помощью OpenAI Whisper
- Возврат текстового файла пользователю

## Требования

- Python 3.13+
- Docker и Docker Compose
- OpenAI API ключ
- Telegram Bot Token

## Установка и запуск

1. Клонируйте репозиторий:
```bash
git clone https://github.com/your-username/transcriber-bot.git
cd transcriber-bot
```

2. Создайте файл `.env` в корневой директории:
```
OPENAI_API_KEY=your_openai_api_key
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
```

3. Запустите с помощью Docker Compose:
```bash
docker-compose up -d
```

## Использование

1. Найдите бота в Telegram по имени, которое вы указали при создании
2. Отправьте команду `/start` для начала работы
3. Отправьте MP3 файл боту
4. Укажите желаемое имя для текстового файла
5. Получите готовый текстовый файл с транскрипцией

## Команды бота

- `/start` - начать работу с ботом
- `/help` - получить инструкции по использованию

## Разработка

Для локальной разработки:

1. Создайте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # для Linux/Mac
# или
venv\Scripts\activate  # для Windows
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Запустите бота:
```bash
python bot.py
``` 