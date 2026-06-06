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
После запуска интерактивная документация API (Swagger UI) будет доступна по адресу: `http://127.0.0`

## Разработка (Команды Makefile)
В проекте настроен `Makefile` для автоматизации проверок кода.
*   `make format` — автоматически исправить форматирование кода с помощью Ruff.
*   `make lint` — проверить код на ошибки и соответствие стилю.
*   `make check` — запустить полную проверку стиля кода перед коммитом.

## Запуск в Docker

Для быстрой сборки зависимостей внутри контейнера используется `uv`.

**Сборка Docker-образа:**
```bash
docker build -t meeting-room-booking .
```

**Запуск приложения в фоновом режиме:**
```bash
docker run -d -p 8000:8000 --name meeting-room-container meeting-room-booking
```

**Просмотр логов приложения:**
```bash
docker logs -f meeting-room-container
```

**Остановка и удаление приложения:**
```bash
docker stop meeting-room-container && docker rm meeting-room-container
```

## Проверка эндпоинтов

*   Проверка статуса сервиса: `curl http://localhost:8000/`
*   Получение списка переговорных комнат: `curl http://localhost:8000/rooms`

## Структура проекта
*   `app/` — исходный код веб-сервиса (FastAPI).
*   `tests/` — автоматические юнит-тесты (Pytest).
*   `pyproject.toml` & `poetry.lock` — конфигурация проекта и фиксация версий зависимостей.
*   `Makefile` — команды для линтера и форматирования.
*   `Dockerfile` — инструкция для сборки Docker-образа.
