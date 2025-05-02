# FastAPI Template 🚀

Шаблон проекта на FastAPI с готовой настройкой базы данных, авторизации и Docker.

## ⚙️ Установка и запуск

### 1. Клонирование репозитория
```bash
git clone https://github.com/kadify-dev/fastapi_template.git
cd fastapi_template/
```

### 2. Создание виртуального окружения через uv
```bash
uv venv
source .venv/Scripts/activate
```

### 3. Установка зависимостей
```bash
uv pip install -r requirements.txt
```

### 4. Настройка переменных окружения
Создайте файл `.env` на основе `.env.example` и укажите свои значения.
Пример:
```env
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASS=postgres
DB_NAME=my_db

SECRET_KEY=SECRET_SECRET
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=30

LOG_LEVEL=ERROR

PGADMIN_DEFAULT_EMAIL=admin@admin.com
PGADMIN_DEFAULT_PASSWORD=admin
```
---

## 🛠️ Работа с Базой Данных

**Применение миграций:**

```bash
alembic upgrade head
```
---

## 🚀 Запуск проекта

### Локально
```bash
uvicorn app.main:app --reload
```

### Через Docker
```bash
docker compose up --build
```
---

## 🚀 Запуск тестов

```bash
pytest
```
