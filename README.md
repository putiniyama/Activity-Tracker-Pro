# Трекер активности

Система мониторинга активности сотрудников в Telegram чатах с веб-интерфейсом.

## Возможности

- 📊 **Мониторинг в реальном времени** - отслеживание времени ответа на сообщения
- ⏰ **Умные уведомления** - автоматические напоминания при превышении времени ответа (15, 30, 60 минут)
- 📈 **Детальная аналитика** - ежедневные, еженедельные и ежемесячные отчеты
- 🔐 **Авторизация через Telegram** - простой вход без необходимости создавать отдельный аккаунт
- 📋 **Экспорт в Google Sheets** - выгрузка статистики для дополнительного анализа
- 👥 **Разграничение прав** - администраторы и обычные сотрудники

## Требования

- Python 3.8+
- PostgreSQL
- Telegram Bot Token
- Google Cloud Service Account (опционально, для экспорта в Google Sheets)

## Установка

1. **Клонируйте репозиторий:**
```bash
git clone <repository-url>
cd employee-activity-tracker
```

2. **Создайте виртуальное окружение:**
```bash
python -m venv venv
source venv/bin/activate  # На Windows: venv\Scripts\activate
```

3. **Установите зависимости:**
```bash
pip install -r requirements.txt
```

4. **Создайте файл `.env` на основе `.env.example`:**
```bash
cp .env.example .env
```

5. **Настройте переменные окружения в `.env`:**
```env
# Telegram Bot
BOT_TOKEN=your_bot_token_here
ADMIN_CHAT_ID=your_admin_chat_id

# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost/employee_tracker

# Web App
SECRET_KEY=your-secret-key-here

# Google Sheets (опционально)
GOOGLE_SHEETS_ENABLED=false
GOOGLE_SHEETS_CREDENTIALS_FILE=credentials.json
SPREADSHEET_ID=your_spreadsheet_id
```

6. **Создайте базу данных PostgreSQL:**
```sql
CREATE DATABASE employee_tracker;
```

## Настройка Telegram бота

1. Создайте бота через [@BotFather](https://t.me/botfather)
2. Получите токен бота и добавьте его в `.env`
3. Добавьте бота в группы, где нужно отслеживать активность
4. Дайте боту права администратора в группах

## Настройка Google Sheets (опционально)

1. Создайте проект в [Google Cloud Console](https://console.cloud.google.com)
2. Включите Google Sheets API
3. Создайте Service Account и скачайте JSON файл с ключами
4. Сохраните файл как `credentials.json` в корне проекта
5. Создайте Google Таблицу и скопируйте её ID из URL
6. Добавьте Service Account email как редактора таблицы

## Запуск

### Запуск бота:
```bash
python -m bot.main
```

### Запуск веб-сервера:
```bash
python -m web.main
```

Или используйте uvicorn напрямую:
```bash
uvicorn web.main:app --host 0.0.0.0 --port 8000 --reload
```

## Первоначальная настройка

1. **Создайте первого администратора через SQL:**
```sql
INSERT INTO employees (telegram_id, full_name, is_admin, is_active) 
VALUES (YOUR_TELEGRAM_ID, 'Admin Name', true, true);
```

2. **Войдите в веб-панель:**
- Откройте http://localhost:8000
- Используйте ваш Telegram ID для входа

3. **Добавьте сотрудников:**
- Перейдите в раздел "Сотрудники"
- Добавьте новых сотрудников с их Telegram ID

## Использование

### Для сотрудников:
- Бот автоматически отслеживает сообщения в группах
- Отправляет уведомления при долгом отсутствии ответа
- Команды в боте:
  - `/start` - Начало работы
  - `/stats` - Статистика за сегодня
  - `/help` - Помощь

### Для администраторов:
- Полный доступ к веб-панели
- Управление сотрудниками
- Просмотр общей статистики
- Экспорт данных в Google Sheets

## Структура проекта

```
tgbot/
├── bot/                  # Telegram бот
│   ├── main.py          # Основной файл бота
│   ├── handlers.py      # Обработчики команд
│   ├── analytics.py     # Сервис аналитики
│   ├── notifications.py # Сервис уведомлений
│   └── scheduler.py     # Планировщик задач
├── web/                 # Веб-приложение
│   ├── main.py         # FastAPI приложение
│   ├── auth.py         # Аутентификация
│   ├── routers/        # API роутеры
│   ├── templates/      # HTML шаблоны
│   └── static/         # Статические файлы
├── database/           # База данных
│   ├── models.py       # Модели SQLAlchemy
│   └── database.py     # Подключение к БД
└── config/             # Конфигурация
    └── config.py       # Настройки приложения
```

## Безопасность

- Используйте сильный `SECRET_KEY` для JWT токенов
- Настройте HTTPS для production
- Ограничьте доступ к базе данных
- Регулярно обновляйте зависимости

## Поддержка

При возникновении проблем:
1. Проверьте логи бота и веб-сервера
2. Убедитесь, что все переменные окружения настроены правильно
3. Проверьте права бота в Telegram группах

## Лицензия

MIT License 