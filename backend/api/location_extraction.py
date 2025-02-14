import spacy
from geopy.geocoders import Nominatim

# Sprachmodell für deutsche Texte
nlp = spacy.load("de_core_news_sm")

# Geolocator für echte Ortsnamen
geolocator = Nominatim(user_agent="hylia_location_extractor")

# Wörter, die fälschlicherweise als Orte erkannt werden
IGNORED_LOCATIONS = {
    "Mehrfamilienhaus", "Schmierereien", "Sachbeschädigungen", "Traktorfahrer",
    "EuroCity", "Königsberger Straße", "Lkr", "Zeugen", "Kaufhaus"
}

def get_location_from_text(text):
    """Extrahiert Straßennamen und Städte aus dem Text und kombiniert sie für eine exakte Geolocation."""
    doc = nlp(text)
    streets = []
    city = None

    for ent in doc.ents:
        if ent.label_ in ["LOC", "GPE"] and ent.text not in IGNORED_LOCATIONS:
            location = geolocator.geocode(ent.text, timeout=5)

            if location:
                # Prüfen, ob es eine Straße oder eine Stadt ist
                if any(word in ent.text.lower() for word in ["straße", "platz", "allee", "ring", "weg"]):
                    streets.append(ent.text)
                else:
                    city = ent.text  # Wenn es eine Stadt ist, speichern

    # Falls eine Straße gefunden wurde, aber keine Stadt, versuchen, eine Stadt zu erkennen
    if streets and not city:
        for ent in doc.ents:
            if ent.label_ == "GPE":
                city = ent.text
                break  # Erste gefundene Stadt nehmen

    # Falls eine Straße und eine Stadt gefunden wurden → Kombinieren für genauere Geolocation
    if streets and city:
        for street in streets:
            full_address = f"{street}, {city}, Deutschland"
            exact_location = geolocator.geocode(full_address, timeout=5)

            if exact_location:
                return {
                    "name": full_address,
                    "lat": exact_location.latitude,
                    "lon": exact_location.longitude
                }

    # Falls nur eine Stadt gefunden wurde
    if city:
        city_location = geolocator.geocode(city, timeout=5)
        if city_location:
            return {
                "name": city,
                "lat": city_location.latitude,
                "lon": city_location.longitude
            }

    return None  # Keine gültige Location gefunden