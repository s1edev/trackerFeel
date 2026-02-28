# Mood Tracker — Telegram Bot

Telegram-бот для отслеживания настроения с AI-анализом и удобной навигацией.

## Возможности

- **Ежедневные напоминания** в 20:30 (локальное время)
- **5 уровней настроения** с эмодзи
- **AI-анализ** через Mistral Large:
  - Выявление паттернов и тенденций
  - Реальные цитаты от известных авторов
- **График настроения** за 30 дней
- **Поиск записей** по дате
- **Inline-навигация** без лишних сообщений

## Команды

| Команда | Описание |
|---------|----------|
| `/start` | Главное меню с inline-кнопками |
| `/graph` | График настроения (через меню) |
| `/day YYYY-MM-DD` | Просмотр записи за дату |

## Быстрый старт

### 1. Установка зависимостей

```bash
pip install -r bot/requirements.txt
```

### 2. Переменные окружения

Создайте `.env` в корне проекта:

```env
BOT_TOKEN=your_telegram_bot_token
MISTRAL_API_KEY=your_mistral_api_key
TIMEZONE=Asia/Yekaterinburg
MOOD_CHECK_TIME=20:30
```

### 3. Запуск

```bash
python bot/main.py
```

## Деплой на Railway

1. Создайте проект на [Railway](https://railway.app)
2. Подключите GitHub-репозиторий
3. Добавьте переменные окружения:
   - `BOT_TOKEN`
   - `MISTRAL_API_KEY`
   - `TIMEZONE` (опционально)
   - `MOOD_CHECK_TIME` (опционально)
4. Railway автоматически запустит бота через `Procfile`

## Структура

```
bot/
├── main.py              # Точка входа
├── config.py            # Конфигурация
├── database.py          # SQLAlchemy сессии
├── models.py            # Модели данных
├── scheduler.py         # APScheduler + рассылки
├── ai_service.py        # Mistral AI интеграция
├── image_generator.py   # Pillow (изображения)
├── graph_service.py     # matplotlib (графики)
├── keyboards.py         # Клавиатуры
├── handlers/
│   ├── start.py         # /start + навигация
│   ├── mood.py          # Запись настроения
│   ├── graph.py         # График
│   └── day.py           # Поиск по дате
├── requirements.txt
└── README.md
```

## Технологии

- Python 3.11+
- aiogram 3.x
- SQLAlchemy + SQLite
- APScheduler
- Pillow
- matplotlib
- Mistral AI SDK

## Лицензия

MIT
