from langchain.tools import tool
from langsmith import traceable
from pymongo import MongoClient
from agent_app.utils.embeddings import EmbeddingClient
from agent_app.utils.calendar import GoogleCalendarClient
from datetime import date, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

_embedder = None
_collection = None
_calendar_client = None


def get_embedder() -> EmbeddingClient:
    global _embedder
    if _embedder is None:
        _embedder = EmbeddingClient()
    return _embedder


def get_collection():
    global _collection
    if _collection is None:
        client = MongoClient(os.getenv("MONGODB_CONNECTION_STRING"))
        _collection = client["agent-rag-duoc-uc"]["embeddings"]
    return _collection


def get_calendar_client() -> GoogleCalendarClient:
    global _calendar_client
    if _calendar_client is None:
        _calendar_client = GoogleCalendarClient()
    return _calendar_client


@traceable(name="retrieve")
def retrieve(query: str, top_k: int = 5) -> list[dict]:
    query_embedding = get_embedder().get_embedding(query)

    results = get_collection().aggregate([
        {
            "$vectorSearch": {
                "index": "vector_index",
                "path": "embedding",
                "queryVector": query_embedding,
                "numCandidates": top_k * 10,
                "limit": top_k,
            }
        },
        {
            "$project": {
                "_id": 0,
                "text": 1,
                "metadata": 1,
                "score": {"$meta": "vectorSearchScore"},
            }
        }
    ])

    return list(results)


@tool
def rag_search(query: str) -> str:
    """Search the class knowledge base to answer questions about the course content."""
    docs = retrieve(query)
    if not docs:
        return "No relevant information found."
    return "\n\n".join(doc["text"] for doc in docs)


WEEKDAYS = {
    "lunes": 0, "martes": 1, "miércoles": 2, "miercoles": 2,
    "jueves": 3, "viernes": 4, "sábado": 5, "sabado": 5, "domingo": 6,
}


@tool
def get_next_date_for_weekday(weekday: str, weeks_ahead: int = 0) -> str:
    """Returns the exact date (YYYY-MM-DD) of a given weekday.
    Args:
        weekday: Day name in Spanish (lunes, martes, miércoles, jueves, viernes, sábado, domingo).
        weeks_ahead: Extra weeks to add. 0 = next occurrence, 1 = in two weeks, 2 = in three weeks, etc.
    """
    weekday = weekday.lower().strip()
    if weekday not in WEEKDAYS:
        return f"Día no reconocido: {weekday}. Usa el nombre en español."
    target = WEEKDAYS[weekday]
    today = date.today()
    days_ahead = (target - today.weekday()) % 7
    if days_ahead == 0:
        days_ahead = 7
    next_date = today + timedelta(days=days_ahead) + timedelta(weeks=weeks_ahead)
    return f"{next_date.strftime('%Y-%m-%d')} ({weekday})"


@tool
def get_available_slots(professor_email: str, date: str) -> str:
    """Get available time slots from the professor's calendar on a given date.
    Args:
        professor_email: Professor's email address.
        date: Date to check in format YYYY-MM-DD.
    """
    slots = get_calendar_client().get_available_slots(professor_email, date)
    if not slots:
        return f"No available slots found on {date}."
    slots_text = "\n".join(f"- {s['start']} to {s['end']}" for s in slots)
    return f"Available slots on {date}:\n{slots_text}"


@tool
def schedule_meeting(summary: str, date: str, start_time: str, end_time: str, attendee_email: str) -> str:
    """Schedule a meeting in Google Calendar.
    Args:
        summary: Title of the meeting.
        date: Date in format YYYY-MM-DD.
        start_time: Start time in format HH:MM.
        end_time: End time in format HH:MM.
        attendee_email: Email of the attendee to invite.
    """
    event = get_calendar_client().create_event(summary, date, start_time, end_time, attendee_email)
    return f"Meeting scheduled: {event.get('htmlLink')}"
