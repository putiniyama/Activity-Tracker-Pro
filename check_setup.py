#!/usr/bin/env python3
"""Проверка настройки системы"""

import asyncio
from database.database import AsyncSessionLocal
from database.models import Employee, SystemSettings
from sqlalchemy import select

async def check_setup():
    async with AsyncSessionLocal() as db:
        print("🔧 ПОЛНАЯ ДИАГНОСТИКА СИСТЕМЫ\n")
        
        # 1. Проверяем сотрудников
        result = await db.execute(select(Employee))
        employees = result.scalars().all()
        
        print("👥 СОТРУДНИКИ В СИСТЕМЕ:")
        for emp in employees:
            print(f"   📛 {emp.full_name}")
            print(f"   🆔 Telegram ID: {emp.telegram_id}")
            print(f"   👤 Username: @{emp.telegram_username}")
            print(f"   ✅ Активен: {'Да' if emp.is_active else 'Нет'}")
            print(f"   👑 Админ: {'Да' if emp.is_admin else 'Нет'}")
            print("   ___")
        
        print(f"📊 Всего сотрудников: {len(employees)}")
        
        # 2. Проверяем настройки уведомлений
        result = await db.execute(select(SystemSettings))
        settings = result.scalars().all()
        settings_dict = {s.key: s.value for s in settings}
        
        print("\n⚙️ НАСТРОЙКИ УВЕДОМЛЕНИЙ:")
        print(f"   🔔 Уведомления включены: {settings_dict.get('notifications_enabled', 'НЕ НАЙДЕНО')}")
        print(f"   ⏰ 1-е уведомление: {settings_dict.get('notification_delay_1', 'НЕ НАЙДЕНО')} мин")
        print(f"   ⏰ 2-е уведомление: {settings_dict.get('notification_delay_2', 'НЕ НАЙДЕНО')} мин")
        print(f"   ⏰ 3-е уведомление: {settings_dict.get('notification_delay_3', 'НЕ НАЙДЕНО')} мин")
        
        # 3. Объясняем логику
        print("\n🎯 КАК РАБОТАЕТ СИСТЕМА:")
        print("   1. Если сообщение от КЛИЕНТА (НЕ из списка сотрудников) → создается уведомление")
        print("   2. Если сообщение от СОТРУДНИКА → уведомления НЕ создаются")
        print("   3. Бот должен быть АДМИНИСТРАТОРОМ в группе")
        
        print("\n❗ ЧАСТЫЕ ПРОБЛЕМЫ:")
        print("   🔸 Человек который пишет УЖЕ добавлен как сотрудник")
        print("   🔸 Бот НЕ администратор в группе")
        print("   🔸 Настройки уведомлений отключены")
        
        # 4. Показываем что нужно проверить
        print("\n✅ ЧТО ПРОВЕРИТЬ:")
        print("   1. Убедитесь что человек НЕ в списке сотрудников выше")
        print("   2. Проверьте что бот АДМИНИСТРАТОР в группе")
        print("   3. Уведомления должны быть включены (true)")
        
        # 5. Показываем ID сотрудников
        employee_ids = [emp.telegram_id for emp in employees]
        print(f"\n🆔 ID СОТРУДНИКОВ: {employee_ids}")
        print("   ☝️ Если ID человека ЕСТЬ в этом списке → он сотрудник, уведомлений НЕ будет!")

if __name__ == "__main__":
    asyncio.run(check_setup()) 