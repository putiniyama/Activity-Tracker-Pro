from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.exceptions import HTTPException
from pydantic import BaseModel
import uvicorn
import aiohttp
import random
from datetime import datetime, timedelta

from config.config import settings
from database.database import init_db, get_db
from database.models import Employee, Message
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from .routers import auth, employees, statistics, dashboard
from .routes import settings as settings_router
from .auth import get_current_user, create_access_token
from web.templates import templates

app = FastAPI(title="Employee Activity Tracker", version="1.0.0")

# CORS настройки
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение статических файлов
app.mount("/static", StaticFiles(directory="web/static"), name="static")

# Шаблоны
templates = Jinja2Templates(directory="web/templates")

# Временное хранилище кодов верификации
verification_codes = {}

class SendCodeRequest(BaseModel):
    telegram_id: int

class VerifyCodeRequest(BaseModel):
    telegram_id: int
    code: str

@app.post("/send-code")
async def send_verification_code(
    request: SendCodeRequest,
    db: AsyncSession = Depends(get_db)
):
    """Отправить код верификации в Telegram"""
    try:
        # Проверяем что пользователь существует
        result = await db.execute(
            select(Employee).where(Employee.telegram_id == request.telegram_id)
        )
        employee = result.scalar_one_or_none()
        
        if not employee:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "Пользователь не найден"}
            )
        
        # Генерируем 6-значный код
        code = str(random.randint(100000, 999999))
        expires_at = datetime.utcnow() + timedelta(minutes=5)
        
        # Сохраняем код
        verification_codes[request.telegram_id] = {
            "code": code,
            "expires_at": expires_at,
            "attempts": 0
        }
        
        # Отправляем код через Telegram Bot API
        bot_token = "8110382002:AAHuWex2O-QvW7ElqyOMu1ZHJEGiS8dSGmE"
        message = f"🔐 Ваш код для входа в систему мониторинга:\n\n<b>{code}</b>\n\n⏰ Код действует 5 минут"
        
        async with aiohttp.ClientSession() as session:
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            data = {
                "chat_id": request.telegram_id,
                "text": message,
                "parse_mode": "HTML"
            }
            async with session.post(url, data=data) as response:
                if response.status == 200:
                    return JSONResponse(content={
                        "success": True, 
                        "message": "Код отправлен в ваш Telegram",
                        "expires_in": 300
                    })
                else:
                    return JSONResponse(
                        status_code=400,
                        content={"success": False, "error": "Ошибка отправки сообщения"}
                    )
                    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": f"Внутренняя ошибка: {str(e)}"}
        )

@app.post("/verify-code")
async def verify_code(
    request: VerifyCodeRequest,
    response: JSONResponse,
    db: AsyncSession = Depends(get_db)
):
    """Проверить код верификации"""
    try:
        # Проверяем наличие кода
        if request.telegram_id not in verification_codes:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "Код не найден или истек"}
            )
        
        stored_data = verification_codes[request.telegram_id]
        
        # Проверяем истечение времени
        if datetime.utcnow() > stored_data["expires_at"]:
            del verification_codes[request.telegram_id]
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "Код истек"}
            )
        
        # Проверяем количество попыток
        if stored_data["attempts"] >= 3:
            del verification_codes[request.telegram_id]
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "Превышено количество попыток"}
            )
        
        # Проверяем код
        if request.code != stored_data["code"]:
            stored_data["attempts"] += 1
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "Неверный код"}
            )
        
        # Код верный - удаляем его и создаем токен
        del verification_codes[request.telegram_id]
        
        # Получаем данные пользователя
        result = await db.execute(
            select(Employee).where(Employee.telegram_id == request.telegram_id)
        )
        employee = result.scalar_one_or_none()
        
        if not employee:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "Пользователь не найден"}
            )
        
        # Создаем токен
        access_token = create_access_token(data={
            "sub": str(employee.telegram_id),
            "employee_id": employee.id,
            "telegram_id": employee.telegram_id,
            "telegram_username": employee.telegram_username,
            "full_name": employee.full_name,
            "is_active": employee.is_active,
            "is_admin": employee.is_admin
        })
        
        # Создаем ответ с токеном в cookies
        redirect_url = "/admin" if employee.is_admin else "/dashboard"
        
        response = JSONResponse(content={
            "success": True,
            "message": "Вход выполнен успешно",
            "redirect": redirect_url,
            "user": {
                "employee_id": employee.id,
                "telegram_id": employee.telegram_id,
                "telegram_username": employee.telegram_username,
                "full_name": employee.full_name,
                "is_active": employee.is_active,
                "is_admin": employee.is_admin,
                "created_at": employee.created_at.isoformat() if employee.created_at else None,
                "updated_at": employee.updated_at.isoformat() if employee.updated_at else None
            }
        })
        
        # Устанавливаем cookie с токеном
        response.set_cookie(
            key="access_token",
            value=access_token,
            max_age=1800,  # 30 минут
            httponly=True,
            secure=False,  # В продакшене должно быть True
            samesite="lax"
        )
        
        return response
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": f"Внутренняя ошибка: {str(e)}"}
        )

@app.get("/logout")
async def logout():
    """Выход из системы"""
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie(key="access_token")
    return response

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request, current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Дашборд для всех пользователей"""
    if current_user.get("is_admin"):
        # Админ видит админскую панель
        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "user": current_user
        })
    else:
        # Сотрудник видит личный кабинет с его статистикой
        # Получаем статистику сотрудника
        today = datetime.utcnow().date()
        start_of_day = datetime.combine(today, datetime.min.time())
        
        # Получаем сообщения сотрудника за сегодня
        messages_result = await db.execute(
            select(Message).where(
                and_(
                    Message.employee_id == current_user.get('employee_id'),
                    Message.received_at >= start_of_day
                )
            ).order_by(Message.received_at.desc()).limit(10)
        )
        recent_messages = messages_result.scalars().all()
        
        # Считаем статистику
        total_messages = len(recent_messages)
        responded_messages = sum(1 for m in recent_messages if m.responded_at is not None)
        missed_messages = total_messages - responded_messages
        
        response_times = [m.response_time_minutes for m in recent_messages if m.response_time_minutes is not None]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        # Превышения времени
        exceeded_15_min = sum(1 for t in response_times if t > 15)
        exceeded_30_min = sum(1 for t in response_times if t > 30)
        exceeded_60_min = sum(1 for t in response_times if t > 60)
        
        stats = {
            'total_messages': total_messages,
            'responded_messages': responded_messages,
            'missed_messages': missed_messages,
            'avg_response_time': avg_response_time,
            'exceeded_15_min': exceeded_15_min,
            'exceeded_30_min': exceeded_30_min,
            'exceeded_60_min': exceeded_60_min
        }
        
        return templates.TemplateResponse("employee_dashboard.html", {
            "request": request,
            "user": current_user,
            "stats": stats,
            "recent_messages": recent_messages
        })

# Подключение роутеров
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(employees.router, prefix="/api/employees", tags=["employees"])
app.include_router(statistics.router, prefix="/api/statistics", tags=["statistics"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])
app.include_router(settings_router.router)  # Настройки системы

# Обработчик ошибок авторизации
@app.exception_handler(HTTPException)
async def auth_exception_handler(request: Request, exc: HTTPException):
    """Обработчик ошибок авторизации - перенаправление на логин только для HTML страниц"""
    # Для API запросов (начинающихся с /api/) возвращаем JSON ошибку
    if request.url.path.startswith("/api/"):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail}
        )
    
    # Для HTML страниц перенаправляем на логин при 401 ошибке
    if exc.status_code == 401 and request.url.path in ["/admin", "/dashboard", "/settings", "/employees", "/statistics"]:
        return RedirectResponse(url="/login?error=" + exc.detail.replace(" ", "%20"), status_code=302)
    
    # Для других ошибок возвращаем стандартный ответ
    raise exc


@app.on_event("startup")
async def startup_event():
    """Инициализация при запуске"""
    await init_db()


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Главная страница - перенаправление на логин"""
    return templates.TemplateResponse("telegram_login.html", {"request": request})


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Страница входа через Telegram"""
    return templates.TemplateResponse("telegram_login.html", {"request": request})


@app.get("/employees", response_class=HTMLResponse)
async def employees_page(request: Request):
    """Страница управления сотрудниками"""
    return templates.TemplateResponse("employees.html", {"request": request})


@app.get("/statistics", response_class=HTMLResponse)
async def statistics_page(request: Request):
    """Страница статистики"""
    return templates.TemplateResponse("statistics.html", {"request": request})


@app.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request):
    """Личный кабинет сотрудника"""
    return templates.TemplateResponse("profile.html", {"request": request})


@app.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    """Страница настроек системы (только для админов)"""
    return templates.TemplateResponse("settings.html", {"request": request})


@app.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request, current_user: dict = Depends(get_current_user)):
    """Админ-панель для управления системой"""
    # Проверяем что пользователь админ
    if not current_user.get("is_admin"):
        # Если не админ - перенаправляем в личный кабинет
        return templates.TemplateResponse("redirect.html", {
            "request": request,
            "redirect_url": "/dashboard",
            "message": "Перенаправление в личный кабинет..."
        })
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": current_user
    })


# Роутер /dashboard обрабатывается в employee.router


@app.get("/health")
async def health_check():
    """Проверка состояния приложения"""
    return {"status": "ok", "message": "Employee Activity Tracker is running"}


@app.get("/test-auth")
async def test_auth(current_user: dict = Depends(get_current_user)):
    """Тестовый endpoint для проверки аутентификации"""
    return {"user": current_user}


if __name__ == "__main__":
    uvicorn.run(
        "web.main:app",
        host=settings.web_host,
        port=settings.web_port,
        reload=True
    ) 