from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from fastapi import FastAPI
from src.tasks.router import router

app = FastAPI()
app.include_router(router)
client = TestClient(app)

SAMPLE_ROW = {
    "id": 1,
    "title": "Ir al gym",
    "description": None,
    "status": "todo",
    "importance": "high",
    "deadline": None,
    "category": "salud",
    "created_at": "2026-06-23T10:00:00+00:00",
    "updated_at": "2026-06-23T10:00:00+00:00",
    "completed_at": None,
}


def mock_supabase(data=None, empty=False):
    mock = MagicMock()
    result = MagicMock()
    result.data = [] if empty else (data or [SAMPLE_ROW])
    chain = mock.table.return_value
    for method in ("select", "insert", "update", "delete", "eq"):
        getattr(chain, method).return_value = chain
    chain.execute.return_value = result
    return mock


def test_list_tasks():
    with patch("src.tasks.router.supabase", mock_supabase()):
        res = client.get("/tasks/")
    assert res.status_code == 200
    assert res.json()[0]["title"] == "Ir al gym"


def test_list_tasks_has_computed_urgency_and_quadrant():
    with patch("src.tasks.router.supabase", mock_supabase()):
        res = client.get("/tasks/")
    task = res.json()[0]
    assert "urgency" in task
    assert "quadrant" in task
    assert task["urgency"] in ("low", "high")
    assert task["quadrant"] in ("Q1", "Q2", "Q3", "Q4")


def test_create_task():
    with patch("src.tasks.router.supabase", mock_supabase()):
        res = client.post("/tasks/", json={
            "title": "Ir al gym",
            "category": "salud",
            "importance": "high",
        })
    assert res.status_code == 201
    assert res.json()["id"] == 1


def test_get_task():
    with patch("src.tasks.router.supabase", mock_supabase()):
        res = client.get("/tasks/1")
    assert res.status_code == 200
    assert res.json()["id"] == 1


def test_get_task_not_found():
    with patch("src.tasks.router.supabase", mock_supabase(empty=True)):
        res = client.get("/tasks/999")
    assert res.status_code == 404


def test_update_task():
    updated = {**SAMPLE_ROW, "title": "Ir al gym actualizado"}
    with patch("src.tasks.router.supabase", mock_supabase(data=[updated])):
        res = client.put("/tasks/1", json={"title": "Ir al gym actualizado"})
    assert res.status_code == 200
    assert res.json()["title"] == "Ir al gym actualizado"


def test_patch_status_to_done():
    done_row = {**SAMPLE_ROW, "status": "done", "completed_at": "2026-06-23T12:00:00+00:00"}
    with patch("src.tasks.router.supabase", mock_supabase(data=[done_row])):
        res = client.patch("/tasks/1/status", json={"status": "done"})
    assert res.status_code == 200
    assert res.json()["status"] == "done"
    assert res.json()["completed_at"] is not None


def test_delete_task():
    with patch("src.tasks.router.supabase", mock_supabase()):
        res = client.delete("/tasks/1")
    assert res.status_code == 204
