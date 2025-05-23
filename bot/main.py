import asyncio
import logging
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from config.config import settings
from database.database import init_db, AsyncSessionLocal
from database.models import Employee, Message as DBMessage, Notification
from .analytics import AnalyticsService
from .notifications import NotificationService
from .handlers import register_handlers

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
bot = Bot(token=settings.bot_token)
dp = Dispatcher()


class MessageTracker:
    def __init__(self):
        self.pending_messages = {}  # {chat_id: {message_id: (employee_id, received_at)}}
        self.analytics = AnalyticsService()
        self.notifications = NotificationService(bot)
    
    async def track_message(self, message: Message, employee_id: int):
        """Отслеживание входящего сообщения от клиента"""
        chat_id = message.chat.id
        message_id = message.message_id
        
        if chat_id not in self.pending_messages:
            self.pending_messages[chat_id] = {}
        
        self.pending_messages[chat_id][message_id] = (employee_id, datetime.utcnow())
        
        # Сохраняем в БД
        async with AsyncSessionLocal() as session:
            db_message = DBMessage(
                employee_id=employee_id,
                chat_id=chat_id,
                message_id=message_id,
                client_username=message.from_user.username,
                client_name=message.from_user.full_name,
                message_text=message.text,
                received_at=datetime.utcnow()
            )
            session.add(db_message)
            await session.commit()
            
            # Запускаем таймеры для уведомлений
            await self.schedule_notifications(db_message.id, employee_id, chat_id)
    
    async def mark_as_responded(self, message: Message, employee_id: int):
        """Отметка сообщения как отвеченного"""
        chat_id = message.chat.id
        
        if chat_id in self.pending_messages:
            # Находим последнее неотвеченное сообщение в этом чате
            for msg_id, (emp_id, received_at) in list(self.pending_messages[chat_id].items()):
                if emp_id == employee_id:
                    response_time = (datetime.utcnow() - received_at).total_seconds() / 60
                    
                    # Обновляем в БД
                    async with AsyncSessionLocal() as session:
                        result = await session.execute(
                            select(DBMessage).where(
                                and_(
                                    DBMessage.chat_id == chat_id,
                                    DBMessage.message_id == msg_id,
                                    DBMessage.employee_id == employee_id
                                )
                            )
                        )
                        db_message = result.scalar_one_or_none()
                        
                        if db_message:
                            db_message.responded_at = datetime.utcnow()
                            db_message.response_time_minutes = response_time
                            await session.commit()
                    
                    # Удаляем из отслеживаемых
                    del self.pending_messages[chat_id][msg_id]
                    
                    # Отменяем запланированные уведомления
                    await self.notifications.cancel_notifications(msg_id)
    
    async def schedule_notifications(self, message_id: int, employee_id: int, chat_id: int):
        """Планирование уведомлений"""
        await self.notifications.schedule_warning(
            message_id, employee_id, chat_id,
            settings.response_time_warning_1, 'warning_15'
        )
        await self.notifications.schedule_warning(
            message_id, employee_id, chat_id,
            settings.response_time_warning_2, 'warning_30'
        )
        await self.notifications.schedule_warning(
            message_id, employee_id, chat_id,
            settings.response_time_warning_3, 'warning_60'
        )


# Создаем экземпляр трекера
message_tracker = MessageTracker()


@dp.message(CommandStart())
async def start_command(message: Message):
    """Обработчик команды /start"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔐 Войти в веб-панель", url=f"http://localhost:{settings.web_port}/auth/telegram?user_id={message.from_user.id}")]
    ])
    
    await message.answer(
        "👋 Добро пожаловать в систему мониторинга активности сотрудников!\n\n"
        "Я помогу отслеживать:\n"
        "• ⏱ Время ответа на сообщения\n"
        "• 📊 Количество обработанных клиентов\n"
        "• ⚠️ Пропущенные сообщения\n"
        "• 📈 Статистику работы\n\n"
        "Используйте кнопку ниже для входа в веб-панель:",
        reply_markup=keyboard
    )


@dp.message(Command("stats"))
async def stats_command(message: Message):
    """Показать статистику сотрудника"""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Employee).where(Employee.telegram_id == message.from_user.id)
        )
        employee = result.scalar_one_or_none()
        
        if not employee:
            await message.answer("❌ Вы не зарегистрированы в системе")
            return
        
        stats = await message_tracker.analytics.get_employee_stats(employee.id, 'daily')
        
        if stats:
            text = f"📊 Ваша статистика за сегодня:\n\n"
            text += f"📨 Всего сообщений: {stats.total_messages}\n"
            text += f"✅ Отвечено: {stats.responded_messages}\n"
            text += f"❌ Пропущено: {stats.missed_messages}\n"
            text += f"⏱ Среднее время ответа: {stats.avg_response_time:.1f} мин\n"
            text += f"⚠️ Ответов > 15 мин: {stats.exceeded_15_min}\n"
            text += f"⚠️ Ответов > 30 мин: {stats.exceeded_30_min}\n"
            text += f"⚠️ Ответов > 60 мин: {stats.exceeded_60_min}"
        else:
            text = "📊 Статистика за сегодня пока отсутствует"
        
        await message.answer(text)


@dp.message(F.chat.type.in_(['group', 'supergroup']))
async def handle_group_message(message: Message):
    """Обработчик сообщений в группах"""
    # Проверяем, является ли сообщение ответом
    if message.reply_to_message:
        # Это ответ сотрудника
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Employee).where(Employee.telegram_id == message.from_user.id)
            )
            employee = result.scalar_one_or_none()
            
            if employee and employee.is_active:
                await message_tracker.mark_as_responded(message, employee.id)
    else:
        # Это новое сообщение от клиента
        # Определяем, кому адресовано сообщение (можно добавить логику распределения)
        # Пока просто трекаем для всех активных сотрудников
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Employee).where(Employee.is_active == True)
            )
            employees = result.scalars().all()
            
            for employee in employees:
                await message_tracker.track_message(message, employee.id)


async def main():
    """Основная функция запуска бота"""
    # Инициализация БД
    await init_db()
    
    # Регистрация обработчиков
    register_handlers(dp, message_tracker)
    
    # Запуск бота
    logger.info("Бот запущен")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main()) 