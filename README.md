# Advanced Dual-Mode Calculator (FastAPI & CLI)

A professional-grade, dual-mode Calculator built in Python featuring a full **CLI REPL** and a **FastAPI Web Server** with a Glassmorphism frontend. Both interfaces share the same modular core logic, organized into clean sub-packages (`core/`, `cli/`, `api/`).

[![CI/CD Pipeline](https://github.com/sairamcharan9/CALCULATOR_WEB_SYSTEMS/actions/workflows/ci.yml/badge.svg)](https://github.com/sairamcharan9/CALCULATOR_WEB_SYSTEMS/actions/workflows/ci.yml)
[![Docker Hub](https://img.shields.io/docker/pulls/sb2853/calculator-web-systems)](https://hub.docker.com/r/sb2853/calculator-web-systems)

---

## 🚀 Features

- **Dual Interaction Modes** — FastAPI SPA and interactive CLI REPL
- **Modular Architecture** — Clean sub-package layout (`app/core`, `app/cli`, `app/api`)
- **10 Arithmetic Operations** — Add, Subtract, Multiply, Divide, Power, Root, Modulus, Int Divide, Percent, Abs Diff
- **Persistent History** — Pandas DataFrame backed by `data/history.csv`; full Undo/Redo via Memento pattern
- **Memory Commands** — Store, Recall, Clear named memory slots
- **Secure User Auth** — SQLAlchemy ORM, bcrypt password hashing, Pydantic v2 validation
- **Calculation BREAD API** — Browse, Read, Edit, Add, Delete calculation records
- **Design Patterns** — Factory, Command, Strategy, Observer, Memento, Facade, Singleton, Plugin
- **288 Tests, 90%+ Coverage** — Unit, CLI, FastAPI integration, and Playwright E2E tests
- **CI/CD** — GitHub Actions → Docker Hub on every push to `main`
- **Containerized** — Docker + Docker Compose (FastAPI + PostgreSQL)

---

## 🛠️ Installation & Setup

```bash
# 1. Clone
git clone https://github.com/sairamcharan9/CALCULATOR_WEB_SYSTEMS.git
cd CALCULATOR_WEB_SYSTEMS

# 2. Virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Dependencies
pip install -r requirements.txt
```

---

## 🌐 FastAPI Web Application

```bash
python main.py          # starts uvicorn on http://127.0.0.1:8000
```

| URL | Description |
|-----|-------------|
| `http://localhost:8000/` | Glassmorphism calculator UI |
| `http://localhost:8000/docs` | Swagger / OpenAPI documentation |
| `http://localhost:8000/redoc` | ReDoc documentation |
| `http://localhost:8000/health` | Health check endpoint |

### Quick API Examples

```bash
# Arithmetic
curl -X POST http://localhost:8000/add \
  -H "Content-Type: application/json" -d '{"a":"10","b":"5"}'

# Register user
curl -X POST http://localhost:8000/users/register \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","email":"alice@example.com","password":"secret"}'

# Login
curl -X POST http://localhost:8000/users/login \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"secret"}'

# Create calculation (BREAD)
curl -X POST http://localhost:8000/calculations/ \
  -H "Content-Type: application/json" \
  -d '{"a":10,"b":5,"type":"ADD","user_id":1}'
```

---

## 💻 CLI REPL

```bash
python main.py --cli
```

```
>>> calc add 10 5
Result: 15.00

>>> calc root 144 2
Result: 12.00

>>> memory store A 999
Stored 999 into memory 'A'.

>>> memory recall A
Recalled A: 999

>>> history
=== Calculation History ===
1. 10 + 5 = 15.00
2. 144 √ 2 = 12.00

>>> undo
Undo successful. 1 calculation(s) remaining.

>>> exit
Goodbye!
```

---

## 🔐 User & Calculation API

### User Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/users/register` | Register a new user (bcrypt hashed) |
| `POST` | `/users/login` | Authenticate (returns user record) |
| `GET` | `/users/{id}` | Get user by ID |
| `GET` | `/users/` | List all users |

### Calculation BREAD Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/calculations/` | Browse all (filter by `?user_id=`) |
| `GET` | `/calculations/{id}` | Read single calculation |
| `POST` | `/calculations/` | Add new calculation (result computed server-side) |
| `PUT` | `/calculations/{id}` | Edit operands/type (result recomputed) |
| `DELETE` | `/calculations/{id}` | Delete calculation |

---

## 🧪 Testing

```bash
# Unit tests (no DB required)
pytest tests/unit -v

# CLI integration tests
pytest tests/cli -v

# FastAPI integration tests (requires PostgreSQL or SQLite fallback)
pytest tests/fastapi/integration -v

# E2E Playwright tests (requires running server on :8000)
python main.py &
playwright install chromium
TEST_URL=http://localhost:8000 pytest tests/fastapi/e2e -v

# Full suite with coverage
pytest tests/unit tests/fastapi/integration tests/cli \
       --cov=app --cov=main --cov-report=term-missing
```

**Current test results: 288 passed across all suites.**

---

## 🐳 Docker

### Single Container

```bash
docker build -t calculator-web .
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:pass@host:5432/db \
  calculator-web
```

### Full Stack (App + PostgreSQL)

```bash
# Copy and configure environment
cp .env.example .env
# Edit .env: set POSTGRES_PASSWORD

docker compose up -d --build
```

| Service | Port | URL |
|---------|------|-----|
| FastAPI app | 8000 | http://localhost:8000 |
| PostgreSQL | 5432 | — |
| pgAdmin 4 | 5050 | http://localhost:5050 |

### Docker Hub

```bash
docker pull sb2853/calculator-web-systems:latest
docker run -p 8000:8000 sb2853/calculator-web-systems:latest
```

---

## 🔄 CI/CD Pipeline

`.github/workflows/ci.yml` runs on every push/PR to `main`:

```
push to main
    │
    ├─► test job (ubuntu + postgres:15)
    │       ├─ pytest tests/unit
    │       ├─ pytest tests/cli
    │       ├─ pytest tests/fastapi/integration
    │       ├─ playwright E2E (chromium, headless)
    │       └─ coverage report → Codecov
    │
    └─► deploy job (main branch only)
            └─ docker build → push sb2853/calculator-web-systems:latest
```

**Required GitHub Secrets**: `DOCKERHUB_USERNAME`, `DOCKERHUB_TOKEN`

---

## 🏗️ Architecture & Design Patterns

| Pattern | Class / Function | Module |
|---------|-----------------|--------|
| **Factory** | `CalculatorFactory` | `app/cli/calculator_factory.py` |
| **Command** | `Calculation`, `CommandManager` | `app/cli/calculation.py`, `app/cli/commands.py` |
| **Strategy** | `@command` decorated operations | `app/cli/operations.py` |
| **Observer** | `LoggingObserver`, `AutoSaveObserver` | `app/cli/history.py` |
| **Memento** | `MementoCaretaker` | `app/cli/calculator_memento.py` |
| **Facade** | `Calculator` REPL | `app/cli/calculator_repl.py` |
| **Singleton** | `command_manager` | `app/cli/command_loader.py` |
| **Plugin** | Dynamic `app/cli/plugins/` loader | `app/__init__.py` |

---

## 📁 Project Structure

```
CALCULATOR_WEB_SYSTEMS/
├── app/
│   ├── __init__.py               # Plugin loader (loads app/cli/plugins/ + operations)
│   ├── core/                     # Shared utilities (no framework deps)
│   │   ├── exceptions.py         # Custom exception hierarchy
│   │   └── logger.py             # Centralized logging setup
│   ├── cli/                      # REPL engine & arithmetic logic
│   │   ├── calculation.py        # Calculation model (Command pattern)
│   │   ├── calculator_config.py  # .env configuration
│   │   ├── calculator_factory.py # Assembles Calculator instance
│   │   ├── calculator_memento.py # Undo/Redo (Memento pattern)
│   │   ├── calculator_repl.py    # REPL facade
│   │   ├── command_loader.py     # Singleton CommandManager instance
│   │   ├── commands.py           # Command registry + @command decorator
│   │   ├── history.py            # History + Observer pattern
│   │   ├── input_validators.py   # Input validation utilities
│   │   ├── interfaces.py         # Abstract base classes
│   │   ├── operations.py         # 10 arithmetic operations (Strategy)
│   │   └── plugins/              # Dynamically loaded plugins
│   │       ├── greet.py
│   │       ├── help.py
│   │       ├── history_commands.py
│   │       └── memory_commands.py
│   └── api/                      # FastAPI / SQLAlchemy layer
│       ├── calculation_routes.py # Calculation BREAD endpoints
│       ├── database.py           # SQLAlchemy engine & session
│       ├── models.py             # User & Calculation ORM models
│       ├── schemas.py            # Pydantic v2 schemas
│       ├── security.py           # bcrypt password hashing
│       └── user_routes.py        # User register/login endpoints
├── templates/
│   └── index.html                # Glassmorphism SPA frontend
├── tests/
│   ├── unit/                     # Unit tests (logic, schemas, security, models)
│   ├── cli/                      # CLI REPL integration tests
│   └── fastapi/
│       ├── integration/          # API integration tests (DB required)
│       └── e2e/                  # Playwright browser tests
├── main.py                       # FastAPI app entrypoint + CLI launcher
├── Dockerfile                    # Production container image
├── docker-compose.yml            # App + PostgreSQL orchestration
├── .github/workflows/ci.yml      # GitHub Actions CI/CD
├── .env.example                  # Environment variable template
├── requirements.txt              # Python dependencies
└── pytest.ini                    # Test configuration
```

---

*Production-ready FastAPI calculator demonstrating enterprise Python architecture — SOLID principles, 10 design patterns, 288 automated tests, full CI/CD pipeline.*
