# Nutze ein leichtgewichtiges Python-Image
FROM python:3.11

# Setze das Arbeitsverzeichnis (root ist jetzt /app)
WORKDIR /app

# Kopiere die Abhängigkeiten und installiere sie
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopiere den gesamten Backend-Code
COPY . .

# Starte die API aus dem richtigen Ordner (backend/api/main.py)
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "5050", "--reload"]