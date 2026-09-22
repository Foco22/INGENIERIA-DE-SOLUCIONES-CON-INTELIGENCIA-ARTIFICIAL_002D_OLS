from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import os
import pickle

SCOPES = ["https://www.googleapis.com/auth/calendar"]
CREDENTIALS_FILE = "credentials.json"
TOKEN_FILE = "token.pickle"
TIMEZONE = "America/Santiago"
TZ = ZoneInfo(TIMEZONE)


class GoogleCalendarClient:
    def __init__(self):
        self.service = self._authenticate()

    def _authenticate(self):
        creds = None
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, "rb") as f:
                creds = pickle.load(f)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
                creds = flow.run_local_server(port=0)
            with open(TOKEN_FILE, "wb") as f:
                pickle.dump(creds, f)

        return build("calendar", "v3", credentials=creds)

    def get_available_slots(self, professor_email: str, date: str, slot_duration: int = 60) -> list[dict]:
        """Returns free slots on a given date using the freebusy API."""
        day_start = datetime.fromisoformat(f"{date}T08:00:00").replace(tzinfo=TZ)
        day_end = datetime.fromisoformat(f"{date}T18:00:00").replace(tzinfo=TZ)

        body = {
            "timeMin": day_start.isoformat(),
            "timeMax": day_end.isoformat(),
            "timeZone": TIMEZONE,
            "items": [{"id": professor_email}],
        }
        result = self.service.freebusy().query(body=body).execute()
        busy_times = result["calendars"].get(professor_email, {}).get("busy", [])

        busy = [
            (
                datetime.fromisoformat(b["start"].replace("Z", "+00:00")).astimezone(TZ),
                datetime.fromisoformat(b["end"].replace("Z", "+00:00")).astimezone(TZ),
            )
            for b in busy_times
        ]

        free_slots = []
        current = day_start
        while current + timedelta(minutes=slot_duration) <= day_end:
            slot_end = current + timedelta(minutes=slot_duration)
            is_busy = any(start < slot_end and end > current for start, end in busy)
            if not is_busy:
                free_slots.append({
                    "start": current.strftime("%H:%M"),
                    "end": slot_end.strftime("%H:%M"),
                })
            current += timedelta(minutes=slot_duration)

        return free_slots

    def create_event(self, summary: str, date: str, start_time: str, end_time: str, attendee_email: str) -> dict:
        event = {
            "summary": summary,
            "start": {"dateTime": f"{date}T{start_time}:00", "timeZone": TIMEZONE},
            "end": {"dateTime": f"{date}T{end_time}:00", "timeZone": TIMEZONE},
            "attendees": [{"email": attendee_email}],
        }
        return self.service.events().insert(calendarId="primary", body=event, sendUpdates="all").execute()
