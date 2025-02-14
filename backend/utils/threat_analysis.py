import spacy

# Laden des NLP-Modells
nlp = spacy.load("de_core_news_sm")

# Schlüsselwörter für Bedrohungslevel
THREAT_KEYWORDS = {
    "hoch": ["Explosion", "Schießerei", "Terror", "Angriff", "Amoklauf", "Geiselnahme"],
    "mittel": ["Razzia", "Messerattacke", "Sprengstoff", "Notfall", "Verletzung", "Brand"],
    "niedrig": ["Polizei", "Zeugen", "Diebstahl", "Sachbeschädigung"]
}

def calculate_threat_level(text):
    """Bestimmt den Threat-Level basierend auf Schlüsselwörtern und NLP."""
    doc = nlp(text.lower())
    threat_score = 0

    for word in doc:
        for level, keywords in THREAT_KEYWORDS.items():
            if word.text in keywords:
                if level == "hoch":
                    threat_score += 3
                elif level == "mittel":
                    threat_score += 2
                else:
                    threat_score += 1

    return min(threat_score, 10)  # Threat-Level von 0-10 normalisieren

def classify_alert_type(threat_level):
    """Weist basierend auf Threat-Level eine Kategorie zu."""
    if threat_level >= 8:
        return "Critical"
    elif threat_level >= 5:
        return "High"
    elif threat_level >= 3:
        return "Medium"
    else:
        return "Low"

def map_severity(threat_level):
    """Mapped den Threat-Level auf eine visuelle Darstellungsform."""
    if threat_level >= 8:
        return "Kritisch"
    elif threat_level >= 5:
        return "Hoch"
    elif threat_level >= 3:
        return "Mittel"
    else:
        return "Niedrig"

def classify_categories(text):
    """Kategorisiert das Ereignis basierend auf Stichworten."""
    categories = []
    if "Terror" in text or "Explosion" in text:
        categories.append("Terrorismus")
    if "Polizei" in text or "Razzia" in text:
        categories.append("Kriminalität")
    if "Feuer" in text or "Brand" in text:
        categories.append("Brandfall")

    return categories if categories else ["Unbekannt"]

def detect_threat_entities(text):
    """Identifiziert relevante Entitäten im Text."""
    doc = nlp(text)
    entities = [ent.text for ent in doc.ents if ent.label_ in ["LOC", "ORG", "PER"]]
    return entities
