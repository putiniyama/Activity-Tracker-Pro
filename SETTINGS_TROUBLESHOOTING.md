# 🔧 Устранение проблемы 404 с настройками

## 🚨 Проблема
При попытке зайти в настройки админ получает ошибку:
```
Failed to load resource: the server responded with a status of 404 (Not Found)
```

## ✅ Диагностика

### 1️⃣ Проверка работы сервера
```bash
# Убедитесь, что веб-сервер запущен
python3 run_web.py

# В консоли должно быть:
# INFO: Uvicorn running on http://0.0.0.0:8000
```

### 2️⃣ Проверка API (работает ✅)
```bash
# Тест без авторизации (должно вернуть "Not authenticated")
curl http://localhost:8000/api/settings/
```

### 3️⃣ Проверка страницы настроек (работает ✅)
```bash
# Страница должна загружаться
curl http://localhost:8000/settings | grep "Настройки системы"
```

## 🎯 Причина проблемы

**API работает**, но требует **авторизации администратора**. 
JavaScript в браузере делает запросы **без токена** или с **неправильным токеном**.

## 🔧 Решение

### Шаг 1: Проверьте авторизацию
1. Откройте **консоль браузера** (F12)
2. Перейдите на вкладку **Application/Storage**
3. Проверьте **Local Storage**:
   - `access_token` - должен существовать
   - `user_info` - должен содержать `is_admin: true`

### Шаг 2: Перелогиньтесь если нужно
Если токена нет или он неправильный:
1. Выйдите из системы (кнопка "Выход")
2. Зайдите заново через Telegram ID: `896737668`

### Шаг 3: Проверьте права админа
```bash
# Диагностика пользователя
python3 check_user.py

# При необходимости пересоздайте админа
python3 simple_init.py
```

## 🛠️ Для разработчика

### Проверка в консоли браузера:
```javascript
// Проверить токен
console.log(localStorage.getItem('access_token'));

// Проверить права
console.log(JSON.parse(localStorage.getItem('user_info') || '{}'));

// Тестовый запрос к API
axios.get('/api/settings/')
  .then(response => console.log('SUCCESS:', response.data))
  .catch(error => console.log('ERROR:', error.response?.status, error.response?.data));
```

### Ожидаемый результат:
- **Токен:** длинная строка JWT
- **user_info:** `{"id": 1, "is_admin": true, "full_name": "Администратор", ...}`
- **API ответ:** `{"notification_delay_1": 15, ...}` 

## 🎯 Если проблема не решена

1. **Остановите все процессы:**
```bash
pkill -f python
```

2. **Перезапустите систему:**
```bash
python3 simple_init.py  # Убедитесь что админ существует
python3 run_web.py      # Запустите веб-сервер
```

3. **Авторизуйтесь заново** с Telegram ID: `896737668`

---

## ✅ Проверочный список

- [ ] Веб-сервер запущен (порт 8000)
- [ ] Страница настроек загружается 
- [ ] В Local Storage есть `access_token`
- [ ] В `user_info` есть `is_admin: true`
- [ ] Консоль браузера не показывает ошибок JS
- [ ] API `/api/settings/` отвечает с токеном

**После выполнения всех пунктов настройки должны работать! 🎉** 