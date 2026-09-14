from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.tasks.router import router as tasks_router
from src.analytics.router import router as analytics_router

app = FastAPI(title="Productivity App API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tasks_router)
app.include_router(analytics_router)


@app.get("/health")
def health():
    return {"status": "ok"}
