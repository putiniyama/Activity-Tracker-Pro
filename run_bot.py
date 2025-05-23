#!/usr/bin/env python3
"""Простой запуск Telegram бота с умным мониторингом"""

import os
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command

# Подключаем новые модули
from bot.notifications import NotificationService
from bot.smart_monitoring import SmartMonitoringService

# Устанавливаем переменные окружения
os.environ["BOT_TOKEN"] = "8110382002:AAHuWex2O-QvW7ElqyOMu1ZHJEGiS8dSGmE"
os.environ["ADMIN_CHAT_ID"] = "896737668"

# Создаём бота
bot = Bot(token=os.environ["BOT_TOKEN"])
dp = Dispatcher()

# Инициализируем сервисы
notification_service = NotificationService(bot)
smart_monitoring = SmartMonitoringService(notification_service)

@dp.message(Command("start"))
async def start_command(message: Message):
    """Обработчик команды /start - ТОЛЬКО в личных сообщениях"""
    # Игнорируем команды в группах
    if message.chat.type != "private":
        return
    
    user_id = message.from_user.id
    web_url = f"http://localhost:8000/login"
    
    text = f"""
👋 Добро пожаловать в систему мониторинга активности сотрудников!

🆔 Ваш Telegram ID: <code>{user_id}</code>

Для входа в систему:
1. Скопируйте ваш Telegram ID
2. Перейдите по ссылке: {web_url}
3. Введите ваш ID для входа

🔧 Функции системы:
• Умный мониторинг времени ответа в группах
• Распознавание адресации (@username, reply)
• Уведомления о задержках (в личку)
• Веб-панель управления и настроек

❓ Команды (только в личных сообщениях):
/start - Это сообщение
/help - Помощь
/stats - Ваша статистика

⚠️ В группах бот работает незаметно - только отслеживает сообщения!

🎯 <b>Умная логика:</b>
• Если клиент пишет @username - уведомление только ему
• Если клиент пишет общее сообщение - уведомление всем активным
• Ответом считается только reply на сообщение клиента
"""
    await message.answer(text, parse_mode="HTML")

@dp.message(Command("help"))
async def help_command(message: Message):
    """Помощь - ТОЛЬКО в личных сообщениях"""
    # Игнорируем команды в группах
    if message.chat.type != "private":
        return
        
    await message.answer("""
🤖 <b>Система умного мониторинга активности</b>

<b>Основные команды (только в личке):</b>
/start - Начало работы
/help - Эта справка
/stats - Ваша статистика

<b>Как это работает:</b>
• В группах: бот НЕЗАМЕТНО отслеживает сообщения
• В личке: отправляет уведомления о задержках
• Веб-панель: детальная статистика и управление

<b>Умная логика уведомлений:</b>
🎯 <b>Клиент пишет @username:</b> уведомление только этому сотруднику
🎯 <b>Клиент пишет общее сообщение:</b> уведомление всем активным
🎯 <b>Ответом считается:</b> только reply на сообщение клиента

<b>Уведомления:</b>
Бот отправит вам в личку уведомление, если вы не ответите клиенту в течение:
• 15 минут ⚠️ (настраивается)
• 30 минут 🚨 (настраивается)
• 60 минут 🔴 (настраивается)

<b>Веб-панель:</b>
Используйте ваш Telegram ID для входа в веб-систему по адресу:
http://localhost:8000/login

<b>Настройки:</b>
Администратор может настроить интервалы уведомлений в веб-панели!
""", parse_mode="HTML")

@dp.message(Command("stats"))
async def stats_command(message: Message):
    """Статистика пользователя - ТОЛЬКО в личных сообщениях"""
    # Игнорируем команды в группах
    if message.chat.type != "private":
        return
        
    user_id = message.from_user.id
    
    text = f"""
📊 <b>Ваша статистика</b>

🆔 Telegram ID: <code>{user_id}</code>
📅 Период: Сегодня

📨 Сообщений обработано: 0
✅ Отвечено вовремя: 0
⚠️ С задержкой: 0
❌ Пропущено: 0

⏱ Среднее время ответа: 0 мин

<i>Для подробной статистики используйте веб-панель:
http://localhost:8000/login</i>

💡 <b>Как добавить бота в рабочую группу:</b>
1. Добавьте бота в группу с клиентами
2. Дайте права администратора (чтобы видел все сообщения)
3. Бот будет незаметно отслеживать ваши ответы
4. Уведомления придут сюда, в личку!

🎯 <b>Умная система:</b>
• Распознает @упоминания и reply
• Уведомляет только нужных сотрудников
• Учитывает только настоящие ответы
"""
    await message.answer(text, parse_mode="HTML")

@dp.message()
async def handle_all_messages(message: Message):
    """Обработчик всех сообщений с умной логикой"""
    
    # В ЛИЧНЫХ сообщениях - помогаем пользователю
    if message.chat.type == "private":
        await message.answer(
            "👋 Используйте команду /start для начала работы с системой мониторинга!\n\n"
            "💡 Не забудьте добавить меня в рабочие группы для отслеживания активности.\n\n"
            "🎯 <b>Умная система</b> распознает адресацию и настоящие ответы!",
            parse_mode="HTML"
        )
        return
    
    # В ГРУППАХ - умный мониторинг
    if message.chat.type in ["group", "supergroup"]:
        # Передаем сообщение в умный сервис мониторинга
        await smart_monitoring.process_message(message)
        return

async def main():
    """Основная функция"""
    print("🤖 Запуск умного Telegram бота...")
    print("📋 Режимы работы:")
    print("   💬 Личные сообщения: команды и уведомления")
    print("   👥 Группы: умный мониторинг с адресацией")
    print("   🎯 Новая логика: @username, reply, общие сообщения")
    print(f"🔗 Веб-панель: http://localhost:8000")
    print("⚙️ Настройки времени уведомлений: в веб-панели")
    
    try:
        await dp.start_polling(bot)
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main()) 