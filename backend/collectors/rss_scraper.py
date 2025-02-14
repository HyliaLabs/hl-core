import json
import logging
import time
import feedparser
from datetime import datetime
from pymongo import MongoClient
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
from config import POLICE_RSS_FEEDS
from update_locations import update_events_with_location  # Automatische Geo-Update-Integration

# Logging einrichten
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# MongoDB-Verbindung
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "hylia_db"
COLLECTION_NAME = "events"

def clean_html(raw_html):
    """Entfernt HTML-Tags aus dem Text und gibt reinen Text zurück."""
    soup = BeautifulSoup(raw_html, "html.parser")
    return soup.get_text()

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

def is_duplicate(title):
    """Überprüft, ob ein Event bereits in der Datenbank existiert."""
    return collection.count_documents({"title": title}) > 0

def extract_datetime(entry):
    """Versucht, das Veröffentlichungsdatum aus dem RSS-Feed zu extrahieren."""
    if hasattr(entry, "published_parsed"):
        return datetime(*entry.published_parsed[:6]).strftime("%Y-%m-%d %H:%M:%S")
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")  # Fallback auf aktuelle Zeit

def parse_rss_feed(url, source_name):
    """Parst einen einzelnen RSS-Feed und speichert relevante Einträge in MongoDB."""
    logging.info(f"Abrufen von {source_name}: {url}")
    try:
        feed = feedparser.parse(url)
    except Exception as e:
        logging.error(f"Fehler beim Abrufen des Feeds von {url}: {e}")
        return

    new_entries = 0
    for entry in feed.entries:
        if is_duplicate(entry.title):
            continue  # Überspringt doppelte Einträge

        event_data = {
            "title": entry.title,
            "summary": entry.summary if "summary" in entry else "",
            "link": entry.link,
            "published": extract_datetime(entry),
            "source": f"{source_name} (rss)",
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        }

        try:
            collection.insert_one(event_data)
            new_entries += 1
        except Exception as e:
            logging.error(f"Fehler beim Speichern des Events in der Datenbank: {e}")

    logging.info(f"{new_entries} neue Einträge aus {source_name} gespeichert.")

def scrape_police_rss():
    """Lädt alle Polizei-RSS-Feeds aus der Config und speichert sie in MongoDB."""
    for country, regions in POLICE_RSS_FEEDS.items():
        for region, url in regions.items():
            parse_rss_feed(url, f"{region} ({country})")

if __name__ == "__main__":
    while True:
        scrape_police_rss()
        logging.info("Füge Geodaten hinzu...")
        update_events_with_location()  # Direkt nach dem Scrapen Geodaten hinzufügen
        logging.info("Warte 5 min, bevor erneut gescraped wird...")
        time.sleep(300)  # 5 Min warten