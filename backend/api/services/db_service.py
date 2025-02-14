import os
import logging
from pymongo import MongoClient, errors
from dotenv import load_dotenv
import datetime

# Lade die Umgebungsvariablen aus der .env-Datei
load_dotenv()

# Logging konfigurieren
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB-Verbindung
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "hylia_db")

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    client.server_info()  # Testet die Verbindung
    logger.info(f"✅ Erfolgreich mit MongoDB verbunden: {MONGO_URI}")
except errors.ServerSelectionTimeoutError as err:
    logger.error(f"❌ Verbindung zu MongoDB fehlgeschlagen: {err}")
    raise

# Datenbank & Collections
db = client[DB_NAME]
events_collection = db["events"]

def insert_event(data: dict) -> str:
    """Fügt ein Ereignis in die Datenbank ein."""
    if "timestamp" not in data:
        data["timestamp"] = datetime.datetime.utcnow()
    try:
        result = events_collection.insert_one(data)
        logger.info(f"📌 Event eingefügt, ID: {result.inserted_id}")
        return str(result.inserted_id)
    except Exception as e:
        logger.error(f"⚠ Fehler beim Einfügen: {e}")
        raise

def get_all_events() -> list:
    """Lädt alle Sicherheitsereignisse ohne _id-Feld."""
    try:
        return list(events_collection.find({}, {"_id": 0}))
    except Exception as e:
        logger.error(f"⚠ Fehler beim Abrufen: {e}")
        return []