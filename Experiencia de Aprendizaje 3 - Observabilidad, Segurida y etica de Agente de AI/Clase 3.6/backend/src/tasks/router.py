from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, HTTPException

from src.database.client import supabase
from src.tasks.schemas import TaskCreate, TaskUpdate, TaskPatch, TaskResponse, CategoryEnum, StatusEnum, ImportanceEnum

router = APIRouter(prefix="/tasks", tags=["tasks"])


def _parse(row: dict) -> TaskResponse:
    return TaskResponse(**row)


@router.get("/", response_model=list[TaskResponse])
def list_tasks(
    status: Optional[StatusEnum] = None,
    category: Optional[CategoryEnum] = None,
    importance: Optional[ImportanceEnum] = None,
):
    query = supabase.table("tasks").select("*")
    if status:
        query = query.eq("status", status)
    if category:
        query = query.eq("category", category)
    if importance:
        query = query.eq("importance", importance)
    result = query.execute()
    return [_parse(row) for row in result.data]


@router.post("/", response_model=TaskResponse, status_code=201)
def create_task(body: TaskCreate):
    data = body.model_dump()
    if data.get("deadline"):
        data["deadline"] = data["deadline"].isoformat()
    result = supabase.table("tasks").insert(data).execute()
    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to create task")
    return _parse(result.data[0])


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int):
    result = supabase.table("tasks").select("*").eq("id", task_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Task not found")
    return _parse(result.data[0])


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, body: TaskUpdate):
    data = {k: v for k, v in body.model_dump().items() if v is not None}
    if "deadline" in data:
        data["deadline"] = data["deadline"].isoformat()
    result = supabase.table("tasks").update(data).eq("id", task_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Task not found")
    return _parse(result.data[0])


@router.patch("/{task_id}/status", response_model=TaskResponse)
def patch_status(task_id: int, body: TaskPatch):
    data: dict = {"status": body.status}
    if body.status == "done":
        data["completed_at"] = datetime.now(timezone.utc).isoformat()
    result = supabase.table("tasks").update(data).eq("id", task_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Task not found")
    return _parse(result.data[0])


@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int):
    result = supabase.table("tasks").delete().eq("id", task_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Task not found")
