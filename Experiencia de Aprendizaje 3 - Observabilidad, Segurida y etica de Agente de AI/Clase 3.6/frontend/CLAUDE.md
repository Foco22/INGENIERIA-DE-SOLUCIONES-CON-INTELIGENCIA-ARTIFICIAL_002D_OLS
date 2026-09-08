# Frontend — Productivity App

## Descripción del proyecto

App de productividad personal con tres módulos principales:

1. **Kanban Board** — gestión de tareas en columnas To Do / Doing / Done
2. **Matriz Impacto-Urgencia** — cuadrante tipo Eisenhower para priorizar tareas
3. **Dashboard Semanal** — análisis y métricas de cumplimiento de tareas

## Stack

- **Framework**: Streamlit (Python)
- **HTTP**: requests
- **Gráficos (dashboard)**: plotly
- **Datos**: pandas
- **Backend**: FastAPI en `../backend` corriendo en `http://localhost:8000`

## Modelo de datos — TaskResponse

Todos los campos que devuelve el backend en cada tarea:

```python
{
  "id": int,                  # int autoincrement (PK)
  "title": str,
  "description": str | None,
  "status": "todo" | "doing" | "done",
  "importance": "low" | "high",
  "deadline": str | None,     # datetime ISO con timezone (ej. "2026-06-25T15:00:00Z")
  "category": "ocio" | "familia" | "salud" | "dinero" | "casa" | "autocuidado" | "amor" | "trabajo",
  "created_at": str,          # datetime ISO
  "updated_at": str,          # datetime ISO — se actualiza automáticamente
  "completed_at": str | None, # datetime ISO — se establece cuando status → "done"

  # Campos computados por el backend (no persisten en BD)
  "urgency": "low" | "high",  # high si deadline <= domingo de la semana actual 23:59:59 UTC
  "quadrant": "Q1" | "Q2" | "Q3" | "Q4"  # calculado desde importance + urgency
}
```

> **Importante:** `urgency` y `quadrant` vienen calculados en cada respuesta del backend.
> El frontend NO debe recalcularlos.

## Cuadrantes de la Matriz (Eisenhower)

| | Urgente | No urgente |
|---|---|---|
| **Importante** | Q1 — Hacer ahora | Q2 — Planificar |
| **No importante** | Q3 — Delegar | Q4 — Eliminar |

Urgencia = `high` cuando `deadline` cae dentro de la semana actual (lunes–domingo).

## Estructura de carpetas

```
frontend/
├── app.py                  # Página home — entrada principal de Streamlit
├── pages/
│   ├── 1_Kanban.py         # Tablero Kanban
│   ├── 2_Matrix.py         # Matriz Eisenhower
│   └── 3_Dashboard.py      # Dashboard semanal
├── services/
│   └── api.py              # Todas las llamadas HTTP al backend
├── requirements.txt
└── CLAUDE.md
```

## Módulos

### 1. Kanban Board (`pages/1_Kanban.py`)
- Tres columnas con `st.columns(3)`: **To Do**, **Doing**, **Done**
- Carga tareas de `GET /tasks/` y las agrupa por `status`
- Cada tarjeta muestra: título, categoría (emoji), importance, deadline
- Filtros en sidebar: categoría e importance
- Botones para mover tarea al siguiente status → usa `PATCH /tasks/{id}/status`
- Formulario con `st.form` para crear / editar tarea

### 2. Matriz Impacto-Urgencia (`pages/2_Matrix.py`)
- Consume `GET /analytics/matrix` — el backend ya devuelve las tareas agrupadas por cuadrante
- Layout 2×2 con `st.columns(2)`
- Cada cuadrante muestra sus tarjetas con título, categoría y deadline
- No calcular urgencia ni quadrant en el cliente

### 3. Dashboard Semanal (`pages/3_Dashboard.py`)
- Consume `GET /analytics/weekly`
- Muestra: tasa de cumplimiento (`st.metric`), tareas por categoría (bar chart), completadas por día (line chart)

## Endpoints del backend (FastAPI — `http://localhost:8000`)

### Tasks

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/tasks/` | Listar tareas. Filtros: `?status=`, `?category=`, `?importance=` |
| POST | `/tasks/` | Crear tarea |
| GET | `/tasks/{task_id}` | Obtener una tarea por ID |
| PUT | `/tasks/{task_id}` | Actualizar tarea completa (todos los campos opcionales) |
| PATCH | `/tasks/{task_id}/status` | Actualizar solo el status |
| DELETE | `/tasks/{task_id}` | Eliminar tarea (204 No Content) |

### Analytics

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/analytics/matrix` | Tareas agrupadas en Q1/Q2/Q3/Q4 |
| GET | `/analytics/weekly` | Estadísticas de los últimos 7 días |

### Health

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/health` | `{"status": "ok"}` |

## Schemas de request

### TaskCreate (POST /tasks/)
```json
{
  "title": "string",
  "description": "string",
  "status": "todo",
  "importance": "low",
  "deadline": "2026-06-25T15:00:00Z",
  "category": "trabajo"
}
```

### TaskUpdate (PUT /tasks/{id})
```json
{
  "title": "string",
  "description": "string",
  "status": "doing",
  "importance": "high",
  "deadline": "2026-06-25T15:00:00Z",
  "category": "salud"
}
```

### TaskPatch (PATCH /tasks/{id}/status)
```json
{ "status": "doing" }
```

## Respuesta de /analytics/matrix

```json
{
  "Q1": [ ],
  "Q2": [ ],
  "Q3": [ ],
  "Q4": [ ]
}
```

## Respuesta de /analytics/weekly

```json
{
  "period": { "start": "2026-06-16", "end": "2026-06-23" },
  "total": 20,
  "completed": 14,
  "completion_rate": 0.70,
  "by_category": {
    "trabajo": { "total": 8, "completed": 6 },
    "salud":   { "total": 5, "completed": 4 }
  },
  "daily_completed": [
    { "date": "2026-06-16", "count": 2 },
    { "date": "2026-06-17", "count": 3 }
  ]
}
```

## Convenciones

- Colores de categoría definidos como emojis en `services/api.py`
- `urgency` y `quadrant` siempre vienen del backend — nunca calcularlos en el cliente
- Un archivo por página en `pages/`

## Puertos

| Servicio | Puerto |
|----------|--------|
| Backend (FastAPI) | `http://localhost:8000` |
| Frontend (Streamlit) | `http://localhost:8501` |

El backend permite CORS desde `http://localhost:8501`.

## Cómo correr

```bash
# Instalar dependencias
pip install -r requirements.txt

# Desarrollo (backend debe estar corriendo en :8000)
streamlit run app.py        # corre en http://localhost:8501
```
