from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from fastapi import FastAPI
from src.analytics.router import router

app = FastAPI()
app.include_router(router)
client = TestClient(app)

BASE_ROW = {
    "id": 1,
    "title": "Tarea",
    "description": None,
    "status": "todo",
    "importance": "high",
    "deadline": None,
    "category": "trabajo",
    "created_at": "2026-06-23T10:00:00+00:00",
    "updated_at": "2026-06-23T10:00:00+00:00",
    "completed_at": None,
}

DONE_ROW = {
    **BASE_ROW,
    "id": 2,
    "status": "done",
    "importance": "low",
    "category": "salud",
    "completed_at": "2026-06-23T12:00:00+00:00",
}


def mock_supabase(rows):
    mock = MagicMock()
    result = MagicMock()
    result.data = rows
    chain = mock.table.return_value
    for method in ("select", "gte", "eq"):
        getattr(chain, method).return_value = chain
    chain.execute.return_value = result
    return mock


def test_matrix_returns_four_quadrants():
    with patch("src.analytics.router.supabase", mock_supabase([BASE_ROW])):
        res = client.get("/analytics/matrix")
    assert res.status_code == 200
    data = res.json()
    assert set(data.keys()) == {"Q1", "Q2", "Q3", "Q4"}


def test_matrix_places_task_in_correct_quadrant():
    with patch("src.analytics.router.supabase", mock_supabase([BASE_ROW])):
        res = client.get("/analytics/matrix")
    data = res.json()
    # BASE_ROW: importance=high, deadline=None → urgency=low → Q2
    assert any(t["id"] == 1 for t in data["Q2"])


def test_weekly_totals():
    with patch("src.analytics.router.supabase", mock_supabase([BASE_ROW, DONE_ROW])):
        res = client.get("/analytics/weekly")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 2
    assert data["completed"] == 1
    assert data["completion_rate"] == 0.5


def test_weekly_has_required_keys():
    with patch("src.analytics.router.supabase", mock_supabase([])):
        res = client.get("/analytics/weekly")
    data = res.json()
    assert {"period", "total", "completed", "completion_rate", "by_category", "daily_completed"} <= set(data.keys())


def test_weekly_by_category_breakdown():
    with patch("src.analytics.router.supabase", mock_supabase([BASE_ROW, DONE_ROW])):
        res = client.get("/analytics/weekly")
    by_cat = res.json()["by_category"]
    assert by_cat["trabajo"]["total"] == 1
    assert by_cat["salud"]["total"] == 1
    assert by_cat["salud"]["completed"] == 1
