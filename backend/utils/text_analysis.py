from sentence_transformers import SentenceTransformer, util

# 🔹 Besseres Transformer-Modell mit größerem Sprachverständnis
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
model = SentenceTransformer(MODEL_NAME)

# 🔹 Verbesserte Sicherheits-Keywords mit Feinabstimmung
SECURITY_KEYWORDS = [
    "Explosion", "Schüsse", "Terroranschlag", "Amoklauf", "Sprengstoff",
    "Messerangriff", "Schießerei", "Geiselnahme", "Bombendrohung",
    "Terrorverdacht", "Attentat", "Anschlag", "Notlage", "Extremismus",
    "Gewaltverbrechen", "Polizeieinsatz", "Großfahndung"
]

# 🔹 Embeddings für die sicherheitsrelevanten Begriffe berechnen
reference_embeddings = model.encode(SECURITY_KEYWORDS, convert_to_tensor=True)

def is_relevant_event(text, threshold=0.55):
    """
    Prüft, ob ein Ereignis sicherheitsrelevant ist, indem es mit Sicherheitsbegriffen verglichen wird.
    - Nutzt semantische Ähnlichkeit mit Sentence-BERT
    - Threshold-Wert (Schwelle) auf 0.55 gesenkt für feinere Erkennung
    """
    text_embedding = model.encode(text, convert_to_tensor=True)
    similarity_scores = util.pytorch_cos_sim(text_embedding, reference_embeddings)

    max_similarity = similarity_scores.max().item()
    return max_similarity >= threshold  # Ereignis wird nur aufgenommen, wenn Ähnlichkeit hoch genug ist