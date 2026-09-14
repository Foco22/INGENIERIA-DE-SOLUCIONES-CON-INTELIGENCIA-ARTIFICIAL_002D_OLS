from collections import defaultdict
from datetime import datetime, timezone, timedelta

from fastapi import APIRouter

from src.database.client import supabase
from src.tasks.schemas import TaskResponse
from src.tasks.utils import compute_urgency, compute_quadrant

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/matrix")
def get_matrix():
    result = supabase.table("tasks").select("*").execute()
    matrix = {"Q1": [], "Q2": [], "Q3": [], "Q4": []}
    for row in result.data:
        task = TaskResponse(**row)
        matrix[task.quadrant].append(task.model_dump())
    return matrix


@router.get("/weekly")
def get_weekly():
    now = datetime.now(timezone.utc)
    week_ago = (now - timedelta(days=7)).isoformat()

    result = supabase.table("tasks").select("*").gte("created_at", week_ago).execute()
    tasks = result.data

    total = len(tasks)
    completed = sum(1 for t in tasks if t["status"] == "done")
    completion_rate = round(completed / total, 2) if total else 0.0

    by_category: dict = defaultdict(lambda: {"total": 0, "completed": 0})
    daily: dict = defaultdict(int)

    for t in tasks:
        cat = t["category"]
        by_category[cat]["total"] += 1
        if t["status"] == "done":
            by_category[cat]["completed"] += 1
            if t.get("completed_at"):
                day = t["completed_at"][:10]
                daily[day] += 1

    daily_completed = [
        {"date": day, "count": count}
        for day, count in sorted(daily.items())
    ]

    return {
        "period": {
            "start": week_ago[:10],
            "end": now.date().isoformat(),
        },
        "total": total,
        "completed": completed,
        "completion_rate": completion_rate,
        "by_category": dict(by_category),
        "daily_completed": daily_completed,
    }
