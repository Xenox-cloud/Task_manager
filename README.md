# Task Manager (FastAPI + React + PostgreSQL)

A small full-stack task manager: a FastAPI REST API, a React frontend, PostgreSQL storage, Docker Compose, pytest tests and a GitHub Actions CI pipeline.

## What it shows

- **Python / FastAPI:** RESTful CRUD API with validation (Pydantic), filtering, search, paging and a stats endpoint.
- **OOP:** a `TaskRepository` class keeps all database code in one place; routes stay thin.
- **Databases:** SQLAlchemy 2.0 models. Works with SQLite (local), PostgreSQL (Docker) or **NeonDB** (set `DATABASE_URL`).
- **React:** hooks-based UI that calls the API (create, filter, search, change status, delete).
- **Docker:** backend image, frontend built and served by nginx, Postgres, all wired with `docker-compose.yml`.
- **Testing + CI/CD:** 8 pytest tests on an in-memory database; GitHub Actions runs tests, a smoke test against real Postgres, the React build and the Docker build.

## API

| Method | Path | Description |
|---|---|---|
| GET | `/api/tasks?status=&search=&limit=&offset=` | List tasks |
| POST | `/api/tasks` | Create a task |
| GET | `/api/tasks/{id}` | Get one task |
| PATCH | `/api/tasks/{id}` | Partial update |
| DELETE | `/api/tasks/{id}` | Delete |
| GET | `/api/tasks/stats` | Counts by status + overdue |

Interactive docs: http://localhost:8000/docs

## Run with Docker

```bash
docker compose up --build
```

Frontend: http://localhost:8080 · API: http://localhost:8000/docs

## Run without Docker

```bash
cd backend
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 (Vite forwards `/api` to port 8000).

## Use NeonDB

Copy `.env.example` to `backend/.env` and set `DATABASE_URL` to your Neon connection string. Tables are created on startup.

## Tests

```bash
cd backend
pytest -q
```

## Deploying to AWS (outline)

Push the two images to Amazon ECR, then run them on ECS Fargate (or App Runner) with `DATABASE_URL` pointing at Amazon RDS for PostgreSQL or NeonDB.
