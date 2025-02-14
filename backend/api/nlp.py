import spacy
from textblob_de import TextBlobDE
import re

# Lade das deutsche Sprachmodell von spaCy
nlp = spacy.load("de_core_news_sm")

# Schlüsselwörter zur Bedrohungseinstufung
THREAT_KEYWORDS = {
    "hoch": ["Explosion", "Terror", "Angriff", "Amoklauf", "Sprengstoff", "Geiselnahme", "Schießerei", "Anschlag"],
    "mittel": ["Messerattacke", "Razzia", "Brandstiftung", "Verletzungen", "Schlägerei", "Raubüberfall"],
    "niedrig": ["Diebstahl", "Vandalismus", "Zeugenaufruf", "Unfall", "Sachbeschädigung"]
}

# Quellengewichtung für Glaubwürdigkeit
SOURCE_WEIGHTS = {
    "Polizei": 1.2,
    "Regierung": 1.1,
    "Nachrichtenagentur": 1.0,
    "Soziale Medien": 0.8,
    "Unbekannt": 0.5
}

# Funktion zur Berechnung des Bedrohungslevels basierend auf Textanalyse
def calculate_threat_level(text):
    text_lower = text.lower()
    threat_score = 0

    # Überprüfe Bedrohungs-Schlüsselwörter
    for level, keywords in THREAT_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in text_lower:
                if level == "hoch":
                    threat_score += 3
                elif level == "mittel":
                    threat_score += 2
                elif level == "niedrig":
                    threat_score += 1

    # Sentiment-Analyse mit TextBlobDE
    sentiment = TextBlobDE(text).sentiment.polarity  # Werte zwischen -1 (negativ) und 1 (positiv)
    if sentiment < -0.3:
        threat_score += 2
    elif sentiment < -0.1:
        threat_score += 1

    # Bedrohungslevel normalisieren
    if threat_score >= 5:
        return "hoch"
    elif 3 <= threat_score < 5:
        return "mittel"
    else:
        return "niedrig"

# Funktion zur Erkennung von sicherheitsrelevanten Entitäten (z. B. Waffen, Orte)
def detect_threat_entities(text):
    doc = nlp(text)
    entities = {"locations": [], "weapons": [], "people": []}

    for ent in doc.ents:
        if ent.label_ in ["LOC", "GPE"]:
            entities["locations"].append(ent.text)
        elif ent.label_ in ["WEAPON", "ORG"]:  # "WEAPON" existiert nicht direkt in spaCy DE, aber anpassbar
            entities["weapons"].append(ent.text)
        elif ent.label_ == "PER":
            entities["people"].append(ent.text)

    return entities

# Funktion zur Kategorisierung von Ereignissen
def classify_categories(text):
    if any(word in text for word in THREAT_KEYWORDS["hoch"]):
        return ["Terrorismus", "Gewalttat"]
    elif any(word in text for word in THREAT_KEYWORDS["mittel"]):
        return ["Kriminalität", "Polizeieinsatz"]
    elif any(word in text for word in THREAT_KEYWORDS["niedrig"]):
        return ["Sachbeschädigung", "Zeugenaufruf"]
    else:
        return ["Sonstiges"]

# Funktion zur Zuordnung der Bedrohungsschwere
def map_severity(threat_level):
    severity_map = {
        "hoch": "urgent",
        "mittel": "elevated",
        "niedrig": "low"
    }
    return severity_map.get(threat_level, "unknown")

# Funktion zur Klassifizierung von Alarmtypen
def classify_alert_type(threat_level):
    alert_types = {
        "hoch": "critical",
        "mittel": "warning",
        "niedrig": "info"
    }
    return alert_types.get(threat_level, "info")