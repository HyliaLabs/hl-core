from pymongo import MongoClient
import folium
from folium.plugins import HeatMap

# 🔹 Verbindung zu MongoDB
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "hylia_db"
COLLECTION_NAME = "events"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

def get_heatmap_data():
    """Lädt ALLE Events mit Location für die Heatmap und Marker."""
    events = list(collection.find(
        {"location": {"$exists": True}},  # Nur Events mit Standort
        {
            "_id": 0,       # `_id` entfernen
            "text": 1,      # Event-Text
            "location": 1,  # Standort-Daten
            "timestamp": 1, # Zeitstempel
            "source": 1     # Quelle (z.B. "x", "telegram", "rss")
        }
    ))
    return events

def generate_map():
    """Erstellt die interaktive Heatmap mit kleinen lila Punkten als Marker."""
    events = get_heatmap_data()
    
    # 🔹 Mittelwert für den Kartenausschnitt berechnen
    if not events:
        map_center = [51.1657, 10.4515]  # Standard (Deutschland)
    else:
        avg_lat = sum(e["location"]["lat"] for e in events) / len(events)
        avg_lon = sum(e["location"]["lon"] for e in events) / len(events)
        map_center = [avg_lat, avg_lon]

    # 🔹 Karte erstellen
    m = folium.Map(location=map_center, zoom_start=5)

    # 🔥 Heatmap-Daten vorbereiten
    heat_data = [(e["location"]["lat"], e["location"]["lon"]) for e in events]

    # 🔹 Heatmap zur Karte hinzufügen
    HeatMap(heat_data, radius=15).add_to(m)

    # 📌 Marker als kleine lila Punkte hinzufügen
    for event in events:
        folium.CircleMarker(
            location=[event["location"]["lat"], event["location"]["lon"]],
            radius=2,  # Größe des Punkts
            color="#81FCF7 ",  
            fill=True,
            fill_color="#81FCF7",  
            fill_opacity=0.2,
            popup=folium.Popup(f"<b>{event['text']}</b><br><i>{event.get('timestamp', 'Kein Datum')}</i><br>Quelle: {event.get('source', 'Unbekannt')}", max_width=250),
        ).add_to(m)

    # 🔹 Karte als HTML speichern
    m.save("../frontend/hylia-frontend/templates/heatmap.html")

if __name__ == "__main__":
    generate_map()
    print("✅ Heatmap mit lila Punkten wurde generiert!")