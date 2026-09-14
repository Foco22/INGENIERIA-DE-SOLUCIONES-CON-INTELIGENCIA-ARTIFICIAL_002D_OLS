from datetime import datetime, timezone, timedelta
from typing import Literal, Optional


def compute_urgency(deadline: Optional[datetime]) -> Literal["low", "high"]:
    if deadline is None:
        return "low"
    now = datetime.now(timezone.utc)
    days_until_sunday = 6 - now.weekday()
    end_of_week = (now + timedelta(days=days_until_sunday)).replace(
        hour=23, minute=59, second=59, microsecond=0
    )
    if deadline.tzinfo is None:
        deadline = deadline.replace(tzinfo=timezone.utc)
    return "high" if deadline <= end_of_week else "low"


def compute_quadrant(
    importance: Literal["low", "high"],
    urgency: Literal["low", "high"],
) -> Literal["Q1", "Q2", "Q3", "Q4"]:
    if importance == "high" and urgency == "high":
        return "Q1"
    if importance == "high" and urgency == "low":
        return "Q2"
    if importance == "low" and urgency == "high":
        return "Q3"
    return "Q4"
