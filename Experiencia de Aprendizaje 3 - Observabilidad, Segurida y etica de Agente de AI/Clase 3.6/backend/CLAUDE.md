# Productivity App — Backend (FastAPI)

## Project Overview

A personal productivity application with Kanban task management, an impact/urgency matrix (Eisenhower), and a weekly completion dashboard.

## Skill

Before starting, apply the senior backend skill to load coding standards and best practices:

```bash
npx claude-code-templates@latest --skill development/senior-backend
```

## Tech Stack

- **Framework:** FastAPI (Python 3.11+)
- **Database:** Supabase (PostgreSQL) via `supabase-py` client — NO SQLAlchemy, NO Alembic
- **Validation:** Pydantic v2
- **Testing:** pytest + httpx (FastAPI TestClient) + unittest.mock to mock the Supabase client
- **CORS:** enabled for React frontend on `http://localhost:5173`

## Monorepo Layout

This backend lives at `Clase 3.6/backend/`. The React frontend is at `Clase 3.6/frontend/` (sibling folder). Both are developed independently and communicate via HTTP.

```
Clase 3.6/
├── backend/      ← you are here (FastAPI, port 8000)
└── frontend/     ← React app (Vite, port 5173)
```

The frontend will call `http://localhost:8000` — CORS must allow `http://localhost:5173`.

---

## Development Workflow (Step-by-Step)

**Build one domain at a time. Do not advance until the current domain is confirmed working.**

Order of implementation:
1. `src/database/` — engine, session, base
2. `src/tasks/` — model, schemas, router
3. `src/analytics/` — matrix and weekly dashboard router

For each domain:
1. Create the files one by one, showing the user each file as it is written.
2. Run the domain's test: `pytest src/<domain>/test_*.py -v`
3. Show the user the full test output.
4. **Do not move to the next domain until the user confirms the current one works.**
5. If a test fails, stop and fix the error before continuing.

---

## Project Structure

```
backend/
├── CLAUDE.md
├── main.py                        # Entry point: creates app, registers routers
├── requirements.txt
├── .env                           # SUPABASE_URL and SUPABASE_KEY (never commit)
├── .gitignore
└── src/
    ├── database/
    │   ├── __init__.py
    │   ├── client.py              # Supabase client singleton (create_client)
    │   └── test_database.py       # Test: client initializes, env vars present
    ├── tasks/
    │   ├── __init__.py
    │   ├── utils.py               # compute_urgency(), compute_quadrant()
    │   ├── schemas.py             # Pydantic: TaskCreate, TaskUpdate, TaskPatch, TaskResponse
    │   ├── router.py              # CRUD endpoints /tasks — calls supabase.table("tasks")
    │   └── test_tasks.py          # Tests: CRUD mocking supabase client
    └── analytics/
        ├── __init__.py
        ├── router.py              # Endpoints /analytics/matrix and /analytics/weekly
        └── test_analytics.py      # Tests: quadrants, weekly dashboard (mocked)
```

Rule: each domain folder is self-contained — schemas, router, and test all live together. No ORM models — the schema lives in Supabase (defined via SQL in the dashboard).

---

## Data Model

### Task

| Field        | Type                          | Notes                                          |
|--------------|-------------------------------|------------------------------------------------|
| id           | int (PK, autoincrement)       |                                                |
| title        | str                           | required                                       |
| description  | str \| None                   | optional                                       |
| status       | enum: todo / doing / done     | Kanban column                                  |
| importance   | enum: low / high              | set by user                                    |
| deadline     | datetime \| None              | used to compute urgency                        |
| category     | enum (see below)              | task theme                                     |
| created_at   | datetime                      | auto                                           |
| updated_at   | datetime                      | auto on every update (trigger)                 |
| completed_at | datetime \| None              | set automatically when status → done           |
| **urgency**  | **computed, NOT stored**      | `high` if deadline within current week, else `low` |

### Category Enum

`ocio | familia | salud | dinero | casa | autocuidado | amor | trabajo`

### Urgency Rule (computed in Python, never stored)

```python
from datetime import datetime, timezone, timedelta

def compute_urgency(deadline) -> str:
    if deadline is None:
        return "low"
    now = datetime.now(timezone.utc)
    # End of current week = next Sunday at 23:59:59
    days_until_sunday = 6 - now.weekday()  # Monday=0, Sunday=6
    end_of_week = (now + timedelta(days=days_until_sunday)).replace(
        hour=23, minute=59, second=59, microsecond=0
    )
    return "high" if deadline <= end_of_week else "low"
```

### Eisenhower Quadrant (computed, not stored)

| Importance \ Urgency | High Urgency    | Low Urgency   |
|----------------------|-----------------|---------------|
| **High Importance**  | Q1 — Do Now     | Q2 — Schedule |
| **Low Importance**   | Q3 — Delegate   | Q4 — Eliminate|

---

## API Endpoints

### Tasks — `src/tasks/router.py`, prefix `/tasks`

| Method | Path           | Description                                                              |
|--------|----------------|--------------------------------------------------------------------------|
| GET    | `/`            | List all tasks. Query params: `status`, `category`, `importance`, `urgency` |
| POST   | `/`            | Create a task                                                            |
| GET    | `/{id}`        | Get single task                                                          |
| PUT    | `/{id}`        | Full update (edit fields, move Kanban column)                            |
| PATCH  | `/{id}/status` | Quick status change — body: `{ "status": "done" }`                      |
| DELETE | `/{id}`        | Delete task                                                              |

### Analytics — `src/analytics/router.py`, prefix `/analytics`

| Method | Path      | Description                                                                            |
|--------|-----------|----------------------------------------------------------------------------------------|
| GET    | `/matrix` | All tasks grouped by Eisenhower quadrant (Q1–Q4)                                       |
| GET    | `/weekly` | Dashboard: total, completed, rate, by-category breakdown, daily counts last 7 days     |

---

## Implementation Notes

### `src/database/client.py`
- Load `SUPABASE_URL` and `SUPABASE_KEY` from `.env` via `python-dotenv`.
- Export a single `supabase` client instance: `supabase = create_client(SUPABASE_URL, SUPABASE_KEY)`.
- All routers import this singleton.

### `main.py`
- Create FastAPI app, add `CORSMiddleware` allowing `http://localhost:5173`.
- Include routers from `src.tasks.router` and `src.analytics.router`.
- No `create_all` — schema is managed in Supabase dashboard.

### `src/tasks/schemas.py`
- `TaskCreate`, `TaskUpdate`, `TaskPatch` (status only), `TaskResponse`.
- `TaskResponse` includes two computed fields (not in DB):
  - `urgency: Literal["low","high"]` — from `compute_urgency(deadline)`
  - `quadrant: Literal["Q1","Q2","Q3","Q4"]` — from importance + urgency

### `src/tasks/router.py`
- All DB calls use `supabase.table("tasks").<method>().execute()`.
- `PATCH /{id}/status` sets `completed_at` to current UTC ISO string when transitioning to `done`.
- Example patterns:
  ```python
  supabase.table("tasks").select("*").execute()           # list
  supabase.table("tasks").insert({...}).execute()         # create
  supabase.table("tasks").update({...}).eq("id", id).execute()  # update
  supabase.table("tasks").delete().eq("id", id).execute() # delete
  ```

### `src/analytics/router.py`
- `/matrix`: fetch all tasks, compute quadrant per task in Python, group into Q1–Q4.
- `/weekly`: fetch tasks from last 7 days, aggregate in Python (totals, by-category, daily counts).

### Supabase Table SQL

El schema completo está en `backend/schema.sql`. Copiar ese archivo y pegarlo en **Supabase → SQL Editor → Run**.

Campos de la tabla `tasks`: `id`, `title`, `description`, `status`, `importance`, `deadline`, `category`, `created_at`, `updated_at`, `completed_at`.
**`urgency` no existe en la tabla** — se calcula en Python desde `deadline`.

### Analytics response shapes

`GET /analytics/weekly`:
```json
{
  "period": { "start": "2026-06-16", "end": "2026-06-22" },
  "total": 20,
  "completed": 14,
  "completion_rate": 0.70,
  "by_category": { "trabajo": { "total": 8, "completed": 6 } },
  "daily_completed": [{ "date": "2026-06-16", "count": 2 }]
}
```

`GET /analytics/matrix`:
```json
{ "Q1": [...tasks], "Q2": [...tasks], "Q3": [...tasks], "Q4": [...tasks] }
```

---

## Testing Philosophy

- **Tests live next to the code they test**, inside each domain folder. No root-level `tests/` directory.
- Every feature gets a test file in its domain folder (`test_<domain>.py`) created at the same time as the feature.
- Tests use FastAPI's `TestClient` (via `httpx`) and **mock the Supabase client** with `unittest.mock.MagicMock` — never call the real Supabase API.
- Each test file patches `src.database.client.supabase` before the request and asserts on the mock calls.
- Tests run offline and fast, with no credentials required.
- Run all tests: `pytest src/ -v`
- Run one domain: `pytest src/tasks/ -v`

---

## Requirements

```
fastapi
uvicorn[standard]
supabase
pydantic
python-dotenv
pytest
httpx
```

## Environment Setup

`backend/.env` (already created, never commit):

```env
SUPABASE_URL=https://<project-ref>.supabase.co
SUPABASE_KEY=<anon-or-service-role-key>
```

## Running the Server

```bash
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

API docs auto-available at `http://localhost:8000/docs`

---

## Frontend Contract Notes

- React frontend runs on `http://localhost:5173` (Vite default).
- All dates are ISO 8601 strings.
- Enums are lowercase strings matching the Python enum values.
- On `PATCH /{id}/status` send body `{ "status": "done" }`.
