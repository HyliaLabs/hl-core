import spacy
from pymongo import MongoClient
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import logging
import time

# Logging einrichten
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# MongoDB Verbindung
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "hylia_db"
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db["events"]

# Geolocator initialisieren
geolocator = Nominatim(user_agent="hylia_location_extractor", timeout=10)

# Sprachmodell für deutsche Texte
nlp = spacy.load("de_core_news_sm")

# Liste von Begriffen, die KEINE Orte sind
IGNORED_LOCATIONS = {
    "Mehrfamilienhaus", "Schmierereien", "Sachbeschädigungen", 
    "Traktorfahrer", "EuroCity", "Bahnhof", "Kaufhaus", "Zeugen",
    "Polizei", "Notruf", "Krankenhaus", "Feuerwehr", "Gericht", "Einsatzkräfte",
    "Zeugen gesucht", "Einsatz", "Tatort", "Tatverdächtiger"
}

def validate_location(name):
    """Validiert mit Geopy, ob der Ort echt ist."""
    try:
        location = geolocator.geocode(name, timeout=5)
        if location:
            return {
                "name": location.address,
                "lat": location.latitude,
                "lon": location.longitude
            }
    except GeocoderTimedOut:
        logging.warning(f"Timeout beim Geocoding für {name}")
    return None

def get_location_from_text(text):
    """Extrahiert Standorte und filtert falsche Treffer."""
    doc = nlp(text)
    locations = set()  # Set für eindeutige Orte

    for ent in doc.ents:
        if ent.label_ in ["LOC", "GPE"] and ent.text not in IGNORED_LOCATIONS:
            locations.add(ent.text)

    valid_locations = []
    for loc in locations:
        validated = validate_location(loc)
        if validated:
            valid_locations.append(validated)

    # Falls mehrere Orte gefunden → ersten nehmen (beste Treffer)
    if valid_locations:
        return valid_locations[0]
    
    return None  # Keine gültige Location gefunden

def update_events_with_location():
    """Fügt Geo-Koordinaten zu allen Events hinzu, die noch keine haben."""
    events = list(collection.find({"location": {"$exists": False}}))
    logging.info(f"{len(events)} Events ohne Standort gefunden.")

    for event in events:
        text = f"{event.get('title', '')} {event.get('summary', '')}"
        location = get_location_from_text(text)

        if location:
            collection.update_one(
                {"_id": event["_id"]},
                {"$set": {"location": location}}
            )
            logging.info(f"Standort hinzugefügt: {location['name']} ({location['lat']}, {location['lon']})")