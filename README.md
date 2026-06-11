# Meeting Room Booking Service

## Быстрый старт

Проект использует Poetry для управления зависимостями.

### Установка зависимостей и создание окружения
Выполните команду для установки всех необходимых пакетов:
```bash
poetry install
```

### Активация виртуального окружения
```bash
eval $(poetry env activate)
```

### Запуск тестов
Запустите автоматические тесты через Pytest:
```bash
poetry run pytest -v
```

### Локальный запуск приложения
Запустите локальный сервер Uvicorn для разработки:
```bash
poetry run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## Команды Makefile
В проекте настроен `Makefile` для автоматизации проверок кода.
*   `make format` — автоматически исправить форматирование кода с помощью Ruff.
*   `make lint` — проверить код на ошибки и соответствие стилю.
*   `make check` — запустить полную проверку стиля кода перед коммитом.

## Запуск в Docker

**Сборка образа:**
```bash
docker build -t meeting-room-booking .
```

**Запуск контейнера:**
```bash
docker run -d -p 8000:8000 --env-file .env --name meeting-room-container meeting-room-booking
```

**Просмотр логов:**
```bash
docker logs -f meeting-room-container
```

**Остановка и удаление:**
```bash
docker stop meeting-room-container && docker rm meeting-room-container
```


## Примеры работы

**Регистрация сотрудника:**
```bash
curl -X POST http://localhost:8000/users/register \
  -H "Content-Type: application/json" \
  -d '{"login": "ivan", "password": "123456", "role": "employee"}'
```

**Логин и получение JWT-токена:**
```bash
curl -X POST http://localhost:8000/users/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=ivan&password=123456"
```
* Ответ:
```bash
{"access_token": "eyJ...", "token_type": "bearer"}
```

**Создание комнаты (админ):**
```bash
curl -X POST http://localhost:8000/rooms \
  -H "Authorization: Bearer <токен_админа>" \
  -H "Content-Type: application/json" \
  -d '{"name": "Конференц-зал", "capacity": 20}'
```

**Создание слота (админ):**
```bash
curl -X POST http://localhost:8000/slots \
  -H "Authorization: Bearer <токен_админа>" \
  -H "Content-Type: application/json" \
  -d '{"room_id": 1, "time_start": "10:00", "time_end": "11:00"}'
```

**Просмотр доступных комнат на дату:**
```bash
curl "http://localhost:8000/rooms?date=2025-06-20"
```

**Бронирование слота:**
```bash
curl -X POST http://localhost:8000/bookings \
  -H "Authorization: Bearer <токен_сотрудника>" \
  -H "Content-Type: application/json" \
  -d '{"slot_id": 1, "date": "2025-06-20"}'
```

**Отмена бронирования:**
```bash
curl -X DELETE http://localhost:8000/bookings/1 \
  -H "Authorization: Bearer <токен_сотрудника>"
```

## Структура проекта
*   `app/` — исходный код (FastAPI)
*   `tests/` — юнит-тесты (Pytest)
*   `pyproject.toml` & `poetry.lock` — зависимости
*   `Makefile` — автоматизация линтинга
*   `Dockerfile` — инструкция для сборки образа
