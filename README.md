# 🤖 Telegram Bot Employee Tracker

Система мониторинга активности сотрудников через Telegram бот с веб-интерфейсом.

## 🚀 Особенности

- 📊 **Отслеживание статистики** - время ответа, количество сообщений, уникальные клиенты
- ⚠️ **Умные уведомления** - напоминания о неотвеченных сообщениях
- 🗑️ **Учет удаленных сообщений** - удаленные клиентами сообщения не считаются пропущенными
- 🌐 **Веб-интерфейс** - удобная панель управления и аналитики
- 📈 **Экспорт в Google Sheets** - автоматическая синхронизация данных
- 📅 **Ежедневные отчеты** - автоматическая рассылка статистики
- 🔐 **Безопасность** - JWT аутентификация, разделение ролей

## ⚠️ ВАЖНО: Безопасность

**НИКОГДА НЕ КОММИТЬТЕ В GIT:**
- `.env` файл с реальными токенами
- `credentials.json` с ключами Google Sheets
- Файлы с паролями и секретными ключами

## 🐳 Быстрый запуск с Docker

### 1. Подготовка

```bash
# Клонирование репозитория
git clone <your-repo-url>
cd tgbot

# Копирование примера конфигурации
cp .env.example .env
```

### 2. Настройка переменных окружения

Отредактируйте `.env` файл:

```bash
# Telegram Bot (ОБЯЗАТЕЛЬНО!)
BOT_TOKEN=YOUR_BOT_TOKEN_FROM_BOTFATHER
ADMIN_CHAT_ID=YOUR_TELEGRAM_ID

# Database
DATABASE_URL=sqlite+aiosqlite:///./data/bot.db

# Web App (ОБЯЗАТЕЛЬНО!)
SECRET_KEY=your-super-secret-key-minimum-32-characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=43200

# Google Sheets (ОПЦИОНАЛЬНО)
GOOGLE_SHEETS_ENABLED=true
GOOGLE_SHEETS_CREDENTIALS_FILE=credentials.json
SPREADSHEET_ID=your_google_spreadsheet_id

# Application Settings
RESPONSE_TIME_WARNING_1=15
RESPONSE_TIME_WARNING_2=30
RESPONSE_TIME_WARNING_3=60

# Web Server
WEB_HOST=0.0.0.0
WEB_PORT=8000
```

### 3. Google Sheets (опционально)

Если нужна интеграция с Google Sheets:

1. Создайте проект в [Google Console](https://console.cloud.google.com/)
2. Включите Google Sheets API
3. Создайте Service Account
4. Скачайте JSON ключ как `credentials.json`
5. Поделитесь таблицей с email из Service Account

### 4. Запуск

```bash
# Развертывание в одну команду
./deploy.sh

# Или вручную:
docker-compose up -d
```

## 📋 Управление сервисом

```bash
# Развертывание (первый запуск)
./deploy.sh deploy

# Обновление
./deploy.sh update

# Просмотр логов
./deploy.sh logs

# Остановка
./deploy.sh stop

# Перезапуск
./deploy.sh restart
```

## 🌐 Доступ к сервисам

После запуска доступны:

- **Веб-интерфейс**: https://localhost (с SSL)
- **Без SSL**: http://localhost:8000
- **Telegram бот**: @your_bot_username

## 📊 Возможности системы

### Для сотрудников:
- `/start` - начало работы и вход в веб-панель
- `/stats` - личная статистика за день
- `/help` - справка по командам
- Автоматические уведомления о неотвеченных сообщениях
- Ежедневные отчеты с детальной статистикой

### Для администраторов:
- `/admin_stats` - общая статистика по всем сотрудникам
- `/mark_deleted CHAT_ID MESSAGE_ID` - пометить сообщение как удаленное
- Веб-панель с полной аналитикой
- Управление настройками уведомлений
- Ручная отправка ежедневных отчетов

### Веб-интерфейс:
- 📈 **Дашборд** - общая статистика и метрики
- 👥 **Сотрудники** - управление персоналом
- 📊 **Статистика** - детальная аналитика
- ⚙️ **Настройки** - конфигурация системы
- 🗂️ **Экспорт** - выгрузка в Google Sheets

## 🔧 Системные требования

- **Docker** 20.0+
- **Docker Compose** 2.0+
- **Свободное место**: 1GB+
- **RAM**: 512MB+
- **Порты**: 80, 443, 8000

## 📂 Структура проекта

```
tgbot/
├── bot/                    # Telegram бот
│   ├── main.py            # Основной файл бота
│   ├── handlers.py        # Обработчики команд
│   ├── analytics.py       # Аналитика и статистика
│   ├── notifications.py   # Система уведомлений
│   └── scheduler.py       # Планировщик задач
├── web/                   # Веб-интерфейс
│   ├── routes/           # API маршруты
│   ├── templates/        # HTML шаблоны
│   ├── static/          # CSS, JS, изображения
│   └── services/        # Бизнес-логика
├── database/             # База данных
│   ├── models.py        # Модели SQLAlchemy
│   └── database.py      # Подключение к БД
├── config/              # Конфигурация
│   └── config.py       # Настройки приложения
├── docker-compose.yml   # Docker Compose конфигурация
├── Dockerfile          # Docker образ
├── nginx.conf          # Nginx конфигурация
├── deploy.sh           # Скрипт развертывания
└── requirements.txt    # Python зависимости
```

## 🔐 Безопасность

### Что защищено:
- JWT токены для веб-аутентификации
- Все секреты в переменных окружения
- HTTPS с современными протоколами
- Security headers в Nginx
- Непривилегированный пользователь в Docker

### Рекомендации:
1. Используйте сильные пароли и ключи
2. Регулярно обновляйте зависимости
3. Для продакшена используйте Let's Encrypt сертификаты
4. Настройте файрвол на сервере
5. Регулярно делайте бэкапы базы данных

## 🚨 Устранение проблем

### Docker Hub Rate Limit:
```bash
# Если возникла ошибка "toomanyrequests"
# Скрипт автоматически переключится на версию без nginx

# Ручное решение:
docker login  # Авторизуйтесь с бесплатным аккаунтом Docker Hub

# Или используйте версию без nginx:
docker-compose -f docker-compose-no-nginx.yml up -d

# Подробнее: см. DOCKER_TROUBLESHOOTING.md
```

### Бот не отвечает:
```bash
# Проверьте логи
./deploy.sh logs

# Проверьте токен бота
grep BOT_TOKEN .env
```

### Веб-интерфейс недоступен:
```bash
# Проверьте статус контейнеров
docker-compose ps

# Проверьте порты
netstat -tulpn | grep :8000
```

### Ошибки SSL:
```bash
# Перегенерация сертификатов
rm -rf ssl/
./deploy.sh deploy
```

## 📝 Логирование

Логи сохраняются в:
- `./logs/` - файлы логов
- `docker-compose logs` - логи контейнеров

## 🔄 Обновление

```bash
# Автоматическое обновление
./deploy.sh update

# Ручное обновление
git pull
docker-compose build --no-cache
docker-compose up -d
```

## 💾 Бэкап

```bash
# Бэкап базы данных
cp ./data/bot.db ./backup/bot_$(date +%Y%m%d_%H%M%S).db

# Бэкап конфигурации
tar -czf backup_$(date +%Y%m%d_%H%M%S).tar.gz .env credentials.json ssl/
```

## 🤝 Поддержка

При возникновении проблем:

1. Проверьте логи: `./deploy.sh logs`
2. Убедитесь в правильности .env файла
3. Проверьте доступность портов
4. Перезапустите сервисы: `./deploy.sh restart`

## 📄 Лицензия

Приватный проект. Все права защищены.

---

**⚠️ Помните: Безопасность - это приоритет! Никогда не публикуйте реальные токены и ключи.** 