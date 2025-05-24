from aiogram import Bot, Dispatcher
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command, CommandStart
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

from database.database import AsyncSessionLocal
from database.models import Employee
from web.services.statistics_service import StatisticsService

async def start_command(message: Message, bot: Bot):
    """Обработчик команды /start"""
    await message.answer(
        "👋 Добро пожаловать в систему мониторинга активности сотрудников!\n\n"
        "Я помогу отслеживать:\n"
        "• ⏱ Время ответа на сообщения\n"
        "• 📊 Количество обработанных клиентов\n"
        "• ⚠️ Пропущенные сообщения\n"
        "• 📈 Статистику работы\n\n"
        "🔐 <b>Для входа в веб-панель:</b>\n"
        f"1. Откройте: http://localhost:8000/login\n"
        f"2. Введите ваш Telegram ID: <code>{message.from_user.id}</code>\n"
        "3. Получите код в этом чате и введите его\n\n"
        "📊 <b>Команды:</b>\n"
        "/stats - ваша статистика\n"
        "/help - подробная справка",
        parse_mode="HTML"
    )

async def help_command(message: Message):
    """Помощь - ТОЛЬКО в личных сообщениях"""
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

async def stats_command(message: Message):
    """Показать статистику сотрудника через StatisticsService"""
    if message.chat.type != "private":
        return
    async with AsyncSessionLocal() as session:
        # Получаем сотрудника по telegram_id
        result = await session.execute(
            select(Employee).where(Employee.telegram_id == message.from_user.id)
        )
        employee = result.scalar_one_or_none()
        if not employee:
            await message.answer("❌ Вы не зарегистрированы в системе")
            return
        
        # Используем единый сервис статистики
        stats_service = StatisticsService(session)
        
        # Получаем статистику за все периоды
        today_stats = await stats_service.get_employee_stats(employee.id, period="today")
        week_stats = await stats_service.get_employee_stats(employee.id, period="week")
        month_stats = await stats_service.get_employee_stats(employee.id, period="month")
        
        # Форматируем время
        now = datetime.utcnow()
        today = now.date()
        
        text = f"""
📊 <b>Ваша статистика</b>

🆔 Telegram ID: <code>{message.from_user.id}</code>
📅 Дата: {today.strftime('%d.%m.%Y')}

<b>📅 Сегодня:</b>
📨 Сообщений: {today_stats.total_messages}
✅ Отвечено: {today_stats.responded_messages}
❌ Пропущено: {today_stats.missed_messages}
👥 Уникальных клиентов: {today_stats.unique_clients}
⏱ Среднее время: {today_stats.avg_response_time:.1f} мин

<b>📅 За неделю:</b>
📨 Сообщений: {week_stats.total_messages}
✅ Отвечено: {week_stats.responded_messages}
❌ Пропущено: {week_stats.missed_messages}
👥 Уникальных клиентов: {week_stats.unique_clients}
⏱ Среднее время: {week_stats.avg_response_time:.1f} мин

<b>📅 За месяц:</b>
📨 Сообщений: {month_stats.total_messages}
✅ Отвечено: {month_stats.responded_messages}
❌ Пропущено: {month_stats.missed_messages}
👥 Уникальных клиентов: {month_stats.unique_clients}
⏱ Среднее время: {month_stats.avg_response_time:.1f} мин

<i>Для подробной статистики используйте веб-панель:\nhttp://localhost:8000/login</i>

🎯 <b>Умная система:</b>
• Распознает @упоминания и reply
• Уведомляет только нужных сотрудников
• Учитывает только настоящие ответы
"""
        await message.answer(text, parse_mode="HTML")

async def test_daily_reports_command(message: Message):
    """Тестовая команда для отправки ежедневных отчетов (только для админа)"""
    if message.chat.type != "private":
        return
        
    async with AsyncSessionLocal() as session:
        # Проверяем права администратора
        result = await session.execute(
            select(Employee).where(
                Employee.telegram_id == message.from_user.id,
                Employee.is_admin == True
            )
        )
        admin = result.scalar_one_or_none()
        
        if not admin:
            await message.answer("❌ У вас нет прав администратора")
            return
        
        await message.answer("📊 Запускаю отправку ежедневных отчетов...", parse_mode="HTML")
        
        # Импортируем из scheduler
        from .scheduler import send_daily_reports
        from ..main import message_tracker
        
        try:
            await send_daily_reports(message_tracker)
            await message.answer("✅ Ежедневные отчеты отправлены всем сотрудникам!", parse_mode="HTML")
        except Exception as e:
            await message.answer(f"❌ Ошибка при отправке отчетов: {e}", parse_mode="HTML")

def register_commands(dp: Dispatcher, bot: Bot):
    """Регистрация обработчиков команд"""
    dp.message.register(start_command, CommandStart())
    dp.message.register(help_command, Command("help"))
    dp.message.register(stats_command, Command("stats"))
    dp.message.register(test_daily_reports_command, Command("test_reports")) 