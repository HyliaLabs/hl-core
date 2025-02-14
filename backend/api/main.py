from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from datetime import datetime
from utils.threat_analysis import calculate_threat_level, classify_alert_type, map_severity, classify_categories, detect_threat_entities
# FastAPI App initialisieren
app = FastAPI()

# CORS Middleware für den Zugriff vom Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Erlaube alle Domains
    allow_credentials=True,
    allow_methods=["*"],  # Erlaube alle HTTP-Methoden
    allow_headers=["*"],  # Erlaube alle Header
)

# MongoDB Verbindung
MONGO_URI = "mongodb://mongo:27017/"
DB_NAME = "hylia_db"
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
events_collection = db["events"]

@app.get("/")
async def home():
    return {"message": "Hylia API läuft!"}

@app.get("/api/heatmap")
async def get_heatmap():
    """Lädt sicherheitsrelevante Ereignisse für die Heatmap."""
    events = events_collection.find({"location": {"$exists": True, "$ne": None}})

    heatmap_data = []
    for event in events:
        if "location" in event and "lat" in event["location"] and "lon" in event["location"]:
            text = f"{event.get('title', '')} {event.get('summary', '')}"
            threat_level = calculate_threat_level(text)
            detected_entities = detect_threat_entities(text)
            alert_type = classify_alert_type(threat_level)

            heatmap_data.append({
                "event_id": str(event.get("_id")),
                "source": event.get("source", "Unbekannt"),
                "timestamp": event.get("timestamp", ""),
                "location": {
                    "name": event["location"].get("name", "Unbekannt"),
                    "lat": event["location"]["lat"],
                    "lon": event["location"]["lon"]
                },
                "summary": event.get("summary", ""),
                "alert_type": alert_type,
                "threat_level": threat_level,
                "alert_severity": map_severity(threat_level),
                "watchlist": event.get("watchlist", []),
                "categories": classify_categories(text),
                "entities": detected_entities
            })

    return JSONResponse(content={"heatmap": heatmap_data})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5050, reload=True)