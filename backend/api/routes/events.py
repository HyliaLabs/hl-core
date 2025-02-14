from fastapi import APIRouter
from api.services.db_service import get_all_events, insert_event

router = APIRouter()

@router.get("/events")
async def fetch_events():
    """Lädt alle Sicherheitsmeldungen."""
    return {"events": get_all_events()}

@router.post("/events")
async def add_event(event: dict):
    """Fügt eine neue Sicherheitsmeldung hinzu."""
    event_id = insert_event(event)
    return {"message": "Event gespeichert", "event_id": event_id}