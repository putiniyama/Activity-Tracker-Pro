# 🐳 Решение проблем с Docker

## Docker Hub Rate Limit

Если вы столкнулись с ошибкой:
```
toomanyrequests: You have reached your unauthenticated pull rate limit
```

### Автоматическое решение
Скрипт `deploy.sh` автоматически переключится на версию без nginx, которая использует только локально собранные образы.

### Ручные решения

#### 1. Использование версии без nginx
```bash
# Запуск без nginx (без SSL)
docker-compose -f docker-compose-no-nginx.yml up -d

# Доступ к веб-интерфейсу: http://localhost
```

#### 2. Авторизация в Docker Hub (рекомендуется)
```bash
# Создайте бесплатный аккаунт на hub.docker.com
# Затем авторизуйтесь:
docker login

# После авторизации запустите обычное развертывание:
./deploy.sh
```

#### 3. Альтернативные решения

##### Очистка Docker кэша
```bash
docker system prune -a
docker-compose down --rmi all
```

##### Использование другого времени
Docker Hub сбрасывает лимиты каждые 6 часов. Попробуйте позже.

##### Использование VPN
Смените IP-адрес через VPN и попробуйте снова.

## Проверка статуса развертывания

### Проверка контейнеров
```bash
# Обычная версия
docker-compose ps

# Версия без nginx
docker-compose -f docker-compose-no-nginx.yml ps
```

### Просмотр логов
```bash
# Обычная версия
docker-compose logs -f

# Версия без nginx
docker-compose -f docker-compose-no-nginx.yml logs -f

# Логи конкретного сервиса
docker logs tgbot_web
docker logs tgbot_bot
```

### Перезапуск сервисов
```bash
# Перезапуск всех сервисов
./deploy.sh restart

# Ручной перезапуск
docker-compose restart
```

## Переход с версии без nginx на полную версию

После решения проблем с Docker Hub:

```bash
# Остановить версию без nginx
docker-compose -f docker-compose-no-nginx.yml down

# Авторизоваться в Docker Hub
docker login

# Запустить полную версию с nginx
./deploy.sh
```

## Альтернативная настройка SSL

Если nginx недоступен, но нужен SSL:

### Использование Cloudflare Tunnel (бесплатно)
1. Зарегистрируйтесь на cloudflare.com
2. Установите cloudflared
3. Создайте туннель к `localhost:8000`

### Использование Caddy вместо nginx
```dockerfile
# Добавьте в docker-compose-no-nginx.yml
caddy:
  image: caddy:alpine
  ports:
    - "80:80"
    - "443:443"
  volumes:
    - ./Caddyfile:/etc/caddy/Caddyfile
  depends_on:
    - web
```

## Мониторинг ресурсов

```bash
# Использование ресурсов
docker stats

# Дисковое пространство
docker system df

# Очистка неиспользуемых ресурсов
docker system prune
``` 