import os
import logging
from pymongo import MongoClient, errors
from dotenv import load_dotenv
import datetime

# Lade die Umgebungsvariablen aus der .env-Datei (diese sollte im Hauptordner HyliaLabs liegen)
load_dotenv()

# Logging konfigurieren
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Hole den MongoDB-URI aus den Umgebungsvariablen, Standard: localhost
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")

# Versuche, die Verbindung zu MongoDB herzustellen
try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    client.server_info()  # Löst einen Fehler aus, falls keine Verbindung hergestellt werden kann
    logger.info("Erfolgreich mit MongoDB verbunden unter: %s", MONGO_URI)
except errors.ServerSelectionTimeoutError as err:
    logger.error("Verbindung zu MongoDB fehlgeschlagen: %s", err)
    raise

# Definiere die Datenbank und Collection
db = client["hylia_db"]
collection = db["security_reports"]

def insert_data(data: dict) -> str:
    """
    Fügt einen neuen Eintrag in die Collection ein und gibt die ID zurück.
    Falls kein Zeitstempel vorhanden ist, wird dieser automatisch ergänzt.
    """
    if "timestamp" not in data:
        data["timestamp"] = datetime.datetime.utcnow()
    try:
        result = collection.insert_one(data)
        logger.info("Dokument eingefügt, ID: %s", result.inserted_id)
        return str(result.inserted_id)
    except Exception as e:
        logger.error("Fehler beim Einfügen des Dokuments: %s", e)
        raise

def get_all_data() -> list:
    """
    Ruft alle Dokumente aus der Collection ab und gibt sie als Liste zurück.
    Dabei wird das _id-Feld entfernt.
    """
    try:
        return list(collection.find({}, {"_id": 0}))
    except Exception as e:
        logger.error("Fehler beim Abrufen der Daten: %s", e)
        raise

if __name__ == "__main__":
    # Teste die Verbindung, indem die vorhandenen Collections geloggt werden
    logger.info("Collections in der Datenbank: %s", db.list_collection_names())