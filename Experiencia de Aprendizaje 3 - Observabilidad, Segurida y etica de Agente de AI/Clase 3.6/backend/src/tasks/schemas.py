from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, computed_field

from src.tasks.utils import compute_urgency, compute_quadrant

CategoryEnum = Literal["ocio", "familia", "salud", "dinero", "casa", "autocuidado", "amor", "trabajo"]
StatusEnum = Literal["todo", "doing", "done"]
ImportanceEnum = Literal["low", "high"]


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    status: StatusEnum = "todo"
    importance: ImportanceEnum = "low"
    deadline: Optional[datetime] = None
    category: CategoryEnum


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[StatusEnum] = None
    importance: Optional[ImportanceEnum] = None
    deadline: Optional[datetime] = None
    category: Optional[CategoryEnum] = None


class TaskPatch(BaseModel):
    status: StatusEnum


class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: StatusEnum
    importance: ImportanceEnum
    deadline: Optional[datetime]
    category: CategoryEnum
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]

    @computed_field
    @property
    def urgency(self) -> Literal["low", "high"]:
        return compute_urgency(self.deadline)

    @computed_field
    @property
    def quadrant(self) -> Literal["Q1", "Q2", "Q3", "Q4"]:
        return compute_quadrant(self.importance, self.urgency)
