from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .config import settings
from .database import Base, engine, get_db
from .models import TaskStatus
from .repository import TaskRepository
from .schemas import TaskCreate, TaskOut, TaskStats, TaskUpdate


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Task Manager API", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",")],
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_repo(db: Session = Depends(get_db)) -> TaskRepository:
    return TaskRepository(db)


def get_task_or_404(task_id: int, repo: TaskRepository = Depends(get_repo)):
    task = repo.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/tasks", response_model=list[TaskOut])
def list_tasks(
    status: TaskStatus | None = None,
    search: str | None = Query(default=None, max_length=100),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    repo: TaskRepository = Depends(get_repo),
):
    return repo.list(status=status, search=search, limit=limit, offset=offset)


@app.post("/api/tasks", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(data: TaskCreate, repo: TaskRepository = Depends(get_repo)):
    return repo.create(data)


@app.get("/api/tasks/stats", response_model=TaskStats)
def task_stats(repo: TaskRepository = Depends(get_repo)):
    return repo.stats()


@app.get("/api/tasks/{task_id}", response_model=TaskOut)
def get_task(task=Depends(get_task_or_404)):
    return task


@app.patch("/api/tasks/{task_id}", response_model=TaskOut)
def update_task(data: TaskUpdate, task=Depends(get_task_or_404), repo: TaskRepository = Depends(get_repo)):
    return repo.update(task, data)


@app.delete("/api/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task=Depends(get_task_or_404), repo: TaskRepository = Depends(get_repo)):
    repo.delete(task)
