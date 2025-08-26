# 🧠 Coach Trusted - Backend

Welcome to the backend for **Coach Trusted**!
Built with [Django](https://www.djangoproject.com/) and designed with a clean, scalable architecture — perfect for building powerful and maintainable APIs.

[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff) [![CI](https://github.com/animemoeus/coach-trusted-backend/actions/workflows/ci.yml/badge.svg)](https://github.com/animemoeus/coach-trusted-backend/actions/workflows/ci.yml) [![codecov](https://codecov.io/gh/animemoeus/coach-trusted-backend/graph/badge.svg?token=wSIhivRGzV)](https://codecov.io/gh/animemoeus/coach-trusted-backend)

---

## 🚀 Local Development Setup

### 🧰 Requirements

- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)
- A little brainpower (a.k.a. brains) 🧠

> ✨ _Note: This setup is optimized for local development using `docker-compose.local.yml`._

---

## 🛠️ Getting Started

### 1. Clone this Repository

```bash
git clone https://github.com/animemoeus/coach-trusted-backend/
cd coach-trusted-backend
```

### 2. Start the Project

```bash
docker compose -f docker-compose.local.yml up --build
```

---

## 🗃️ Common Management Commands

### 🏗️ Create Migration Files

```bash
docker compose -f docker-compose.local.yml run --rm django python manage.py makemigrations
```

### 🔄 Apply Migrations

```bash
docker compose -f docker-compose.local.yml run --rm django python manage.py migrate
```

### 🧪 Run Tests

```bash
docker compose -f docker-compose.local.yml run --rm django python manage.py test
```

### 💡 Run Other Commands

```bash
docker compose -f docker-compose.local.yml run --rm django python manage.py <your-command>
```

---

## 🧹 Code Quality

This project uses [`ruff`](https://github.com/astral-sh/ruff) to keep your Python code clean and stylish.

Run linting:

```bash
docker compose -f docker-compose.local.yml run --rm django ruff check .
```

---

## 📦 Extra Info

- Django Admin: `http://localhost:8000/admin/`
- API Docs (if added): `http://localhost:8000/api/docs/`

---

## ❤️ Credits

Made with 💻 and love by Coach Trusted Team.
