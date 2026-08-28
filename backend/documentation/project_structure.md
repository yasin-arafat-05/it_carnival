# EduManage API — Project Architecture & Skill Guide

> **LLM Instructions / Context Skill File**: This document serves as the complete architectural blueprint, coding style guide, and project structure specification for the **EduManage API** FastAPI backend. Any LLM or developer working on this repository MUST follow the patterns, import standards, and conventions detailed herein.

---

## 1. Directory Structure

```
backend/
├── app/
│   ├── .env                      # Environment variables configuration file
│   ├── DockerFile                # Multi-stage/Alpine Dockerfile for FastAPI app
│   ├── requirements.txt          # Python dependencies list
│   ├── main.py                   # Application entrypoint & FastAPI initialization
│   ├── lifespan.py               # Async context manager for app startup/shutdown hooks
│   ├── middleware.py             # Request logging & CORS middleware setup
│   ├── core/                     # Core system modules (config, security, dependencies)
│   │   ├── __init__.py
│   │   ├── config.py             # Pydantic Settings & dynamic URL generators
│   │   ├── security.py           # Security module re-exporting auth helpers
│   │   ├── dependencies.py       # Password hashing, JWT creation/verification, user auth
│   │   └── auth.py               # FastAPI dependency `get_current_user`
│   ├── database/                 # Database layer (models, schemas, sessions)
│   │   ├── __init__.py
│   │   ├── base.py               # DeclarativeBase class
│   │   ├── session.py            # Async engine & asyncSession sessionmaker setup
│   │   ├── models/               # SQLAlchemy ORM models
│   │   │   ├── __init__.py
│   │   │   ├── user.py           # User ORM model
│   │   │   └── chat_history.py   # Conversation & MessageHistory ORM models
│   │   └── schemas/              # Pydantic data validation schemas
│   │       ├── __init__.py
│   │       ├── user.py           # UserCreate, UserResponse, TokenResponse schemas
│   │       └── token.py          # Token schema
│   ├── services/                 # Business logic layer
│   │   ├── signup_services.py    # User creation and validation service
│   │   └── login_services.py     # Authentication & JWT issuance service
│   ├── routes/                   # API endpoint controllers
│   │   ├── __init__.py
│   │   ├── auth.py               # Authentication endpoints (/auth/signup)
│   │   ├── login.py              # Login endpoint (/token)
│   │   └── router.py             # Main router aggregating all endpoint sub-routers
│   ├── mcp/                      # Model Context Protocol integrations (future)
│   ├── workflow/                 # LangGraph / AI orchestration workflows (future)
│   └── workers/                  # Celery / background worker tasks (future)
├── documentation/
│   └── project_structure.md      # THIS FILE — Architectural blueprint & LLM skill guide
├── k8s/                          # Kubernetes manifests directory (Deployment, Service, etc.)
├── docker-compose.yml            # Multi-container orchestration (DB, Redis, API servers, Nginx)
├── nginx.conf                    # Nginx reverse proxy & load balancer configuration
└── .python-version               # Python version specification
```

---

## 2. Core Architectural Rules & Conventions

When modifying or expanding this codebase, strictly observe the following rules:

### Rule 1: Import Path Standard
- **ALWAYS** use absolute imports starting with `app.` (e.g., `from app.core.config import CONFIG`, `from app.database.session import asyncSession`).
- **NEVER** prefix imports with `backend.app...` or use relative imports (`..`) across top-level modules.

### Rule 2: Database Access Pattern
- **Async Engine**: Engine created with `create_async_engine(CONFIG.DATABASE_URL, pool_size=20, max_overflow=10, pool_pre_ping=True)`.
- **Session Context**: ALWAYS manage sessions using the `asyncSession` sessionmaker inside an async context manager:
  ```python
  async with asyncSession() as db:
      # perform queries with await db.execute(...)
  ```
- **ORM Base**: Use `app.database.base.Base` which inherits from `sqlalchemy.orm.DeclarativeBase`.

### Rule 3: Security & Auth Architecture
- **`app/core/security.py`** serves as the public interface for security functions (`get_password_hash`, `verify_password`, `verify_token`, `authenticate_user`, `create_access_token`).
- **User Passwords**: Hashed with `pwdlib` (Argon2 algorithm). Hashed column in `User` ORM model is `password_hash` (NOT `password`).
- **Tokens**: Standard JWT containing payload `{"id": str(user.id), "email": user.email}` signed with `CONFIG.SECRET_KEY` using algorithm `CONFIG.ALGORITHM` (HS256).

### Rule 4: Router Structure
- Route endpoints are defined in separate modules inside `app/routes/` (e.g., `auth.py`, `login.py`).
- All sub-routers are registered inside `app/routes/router.py` using `api_router = APIRouter()`.
- `main.py` includes ONLY `api_router` from `app.routes.router`.

---

## 3. Component Details & Reference Implementations

### A. Environment & Configuration (`app/core/config.py`)
Loads values from `app/.env` using Pydantic `BaseSettings`:
- Key configuration variables:
  - `SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`
  - `DB_ROLE_NAME`, `DB_PASSWORD`, `DB_HOST`, `DATABASE`, `DB_PORT`
  - `REDIS_HOST`, `REDIS_PORT`, `REDIS_PASSWORD`
  - `MAIL_USERNAME`, `MAIL_PASSWORD`, `MAIL_FROM`, `MAIL_PORT`, `MAIL_SERVER`
- Dynamically constructs:
  - `CONFIG.DATABASE_URL` -> `postgresql+asyncpg://...`
  - `CONFIG.DATABASE_URL_ALEMBIC` -> `postgresql://...`
  - `CONFIG.REDIS_URL`, `CONFIG.REDIS_CACHE_URL`, `CONFIG.REDIS_DB_LLM_URL`


## 4. Docker & Reverse Proxy Architecture

### Docker Compose (`docker-compose.yml`)
- **`db`**: PostgreSQL 16 Alpine running on internal private network.
- **`redis`**: Redis 7 Alpine with LRU eviction policy.
- **`server1` / `server2`**: Replicated FastAPI instances exposed on internal ports 8000 and 8001.
- **`nginx`**: Nginx proxy listening on port `8080`, routing requests to upstream servers:
  - `/server1/` -> `http://app_server1/`
- **`prometheus` & `grafana`**: System monitoring stack running on separate monitoring network.

---

## 5. Coding Style & Formatting Guidelines for AI Assistants

1. **Comment Preservation**: Retain informative top-of-function and inline comments (e.g., `# oauth2 scheme:`, `# check the token validity:`).
2. **Error Logging**: Print informative debug messages for startup/shutdown and caught service exceptions (`print(f"error while signup: {e}")`).
3. **Pydantic Validation**: Use `from_attributes = True` inside schema `Config` classes to allow seamless conversion from SQLAlchemy ORM instances (`UserResponse.model_validate(user)`).
4. **Type Hints**: Annotate method parameters and return types using standard Python typing (`UUID`, `Optional[str]`, `AsyncSession`, `FastAPI`).
5. **Kubernetes Integration**: Store all K8s manifests (Deployments, Services, Ingress, Secrets) in the root `/k8s/` directory.

---
*End of Specification. Reading this document gives any LLM or developer full mastery of the EduManage API repository.*
