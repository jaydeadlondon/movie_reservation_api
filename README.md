# Movie Reservation API

![Python](https://img.shields.io/badge/python-3.12-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)
![SQLite](https://img.shields.io/badge/database-SQLite-blue.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

Backend система для бронирования билетов в кино на FastAPI + SQLite.

## 🚀 Технологии

- **FastAPI** - современный веб-фреймворк
- **SQLAlchemy** - ORM для работы с БД
- **SQLite** - встроенная база данных (без установки!)
- **Pydantic** - валидация данных
- **JWT** - безопасная аутентификация

## ✨ Функционал

### 👤 Пользователи
- ✅ Регистрация и вход
- ✅ JWT аутентификация
- ✅ Роли (admin, user)

### 🎬 Фильмы (Admin)
- ✅ Создание, редактирование, удаление фильмов
- ✅ Управление сеансами
- ✅ Жанры и описания

### 🎫 Бронирование
- ✅ Просмотр доступных мест
- ✅ Бронирование нескольких мест одновременно
- ✅ Отмена бронирования
- ✅ Защита от overbooking (транзакционная блокировка)

### 📊 Отчёты (Admin)
- ✅ Статистика по бронированиям
- ✅ Заполняемость залов
- ✅ Расчёт выручки

## 📦 Установка

### 1. Клонировать репозиторий

```bash
git clone https://github.com/jaydeadlondon/movies_reservation_api.git
cd movies_reservation_api
```

### 2. Создать виртуальное окружение

```bash
python -m venv venv

venv\\Scripts\\activate # Windows

source venv/bin/activate # Linux/Mac
```

### 3. Установить зависимости

```bash
pip install -r requirements.txt
```

### 4. Создать .env файл

```bash
# Скопировать шаблон
cp .env.example .env
```

**.env:**
```bash
DATABASE_URL=sqlite:///./movie_reservation.db
SECRET_KEY=your-secret-key-here # Измените это
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 5. Создать базу данных и первого админа

```bash
python seed_data.py
```

**Будет создан администратор:**
- **Username:** \`admin\`
- **Password:** \`admin123\`
- **Email:** \`admin@example.com\`


### 6. Запустить сервер

```bash
uvicorn app.main:app --reload
```

**API запущено! 🎉**

- **API:** http://localhost:8000
- **Документация (Swagger):** http://localhost:8000/docs
- **Альтернативная документация (ReDoc):** http://localhost:8000/redoc

## 📝 TODO / Планируемые улучшения

- [ ] Пагинация для списков
- [ ] Фильтры (по жанру, дате, цене)
- [ ] Загрузка файлов (постеры фильмов)
- [ ] Email уведомления о бронировании
- [ ] Интеграция с платёжными системами
- [ ] Rate limiting (защита от spam)
- [ ] Логирование (logs)
- [ ] Unit тесты
- [ ] Docker контейнеризация
- [ ] CI/CD (GitHub Actions)

## 📄 Лицензия

MIT License

## 👤 Автор

**jaydeadlondon**

- GitHub: [@jaydeadlondon](https://github.com/jaydeadlondon)

---

**⭐ Если проект понравился - поставьте звезду!**