# Meeting Room Booking Service

Cервис бронирования переговорных комнат на FastAPI

## Локальный запуск (Poetry)

1. Установка пакетов:
```bash
poetry install
```
2. Запуск тестов:
```bash
poetry run pytest -v
```
3. Запуск сервера:
```bash
poetry run uvicorn app.main:app --reload --host 127.0.0.1 --port 8080
```
*Swagger: http://127.0.0*

## Запуск в Docker

### Вариант 1: Одиночный контейнер (SQLite)
```bash
docker build -t booking-app .
docker run -d -p 8000:8000 --name booking-container booking-app
```
*Swagger: http://localhost:8000/docs*

### Вариант 2: Docker Compose (PostgreSQL)
```bash
docker compose up -d --build
```
*Swagger: http://localhost:8080/docs*

## Автоматизация (Makefile)
*   `make format` — форматирование кода (Ruff)
*   `make lint` — проверка стиля кода
*   `make check` — полная проверка перед коммитом

## Примеры API-запросов (для порта 8080)

**Регистрация:**
```bash
curl -X POST http://localhost:8080/users/register \
  -H "Content-Type: application/json" \
  -d '{"login": "user", "password": "123456", "role": "employee"}'
```

**Авторизация (Получение токена):**
```bash
curl -X POST http://localhost:8080/users/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user&password=123456"
```

**Создание комнаты (Admin):**
```bash
curl -X POST http://localhost:8080/rooms \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"name": "Конференц-зал", "capacity": 20}'
```

**Создание слота (Admin):**
```bash
curl -X POST http://localhost:8080/slots \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"room_id": 1, "time_start": "10:00", "time_end": "11:00"}'
```

**Просмотр доступности комнат:**
```bash
curl "http://localhost:8080/rooms?date=2026-06-20"
```

**Бронирование слота:**
```bash
curl -X POST http://localhost:8080/bookings \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"slot_id": 1, "date": "2026-06-20"}'
```

**Отмена бронирования:**
```bash
curl -X DELETE http://localhost:8080/bookings/1 \
  -H "Authorization: Bearer <TOKEN>"
```
