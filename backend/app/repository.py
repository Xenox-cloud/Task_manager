from datetime import date

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from .models import Task, TaskStatus
from .schemas import TaskCreate, TaskStats, TaskUpdate


class TaskRepository:
    """Keeps all database access for tasks in one place, so routes stay thin."""

    def __init__(self, db: Session):
        self.db = db

    def list(self, status: TaskStatus | None = None, search: str | None = None,
             limit: int = 50, offset: int = 0) -> list[Task]:
        query = select(Task)
        if status:
            query = query.where(Task.status == status)
        if search:
            pattern = f"%{search}%"
            query = query.where(or_(Task.title.ilike(pattern), Task.description.ilike(pattern)))
        query = query.order_by(Task.created_at.desc(), Task.id.desc()).limit(limit).offset(offset)
        return list(self.db.scalars(query))

    def get(self, task_id: int) -> Task | None:
        return self.db.get(Task, task_id)

    def create(self, data: TaskCreate) -> Task:
        task = Task(**data.model_dump())
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def update(self, task: Task, data: TaskUpdate) -> Task:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(task, field, value)
        self.db.commit()
        self.db.refresh(task)
        return task

    def delete(self, task: Task) -> None:
        self.db.delete(task)
        self.db.commit()

    def stats(self) -> TaskStats:
        rows = self.db.execute(select(Task.status, func.count()).group_by(Task.status)).all()
        by_status = {s.value: 0 for s in TaskStatus}
        by_status.update({status.value: count for status, count in rows})
        overdue = self.db.scalar(
            select(func.count()).select_from(Task)
            .where(Task.due_date < date.today(), Task.status != TaskStatus.done)
        )
        return TaskStats(total=sum(by_status.values()), by_status=by_status, overdue=overdue or 0)
