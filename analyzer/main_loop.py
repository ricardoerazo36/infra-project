import os
import json
import glob
import collections
import pandas as pd
from datetime import datetime

CLEAN_DIR = "/app/data/clean"
OUT_DIR = "/app/data/analysis"


os.makedirs(OUT_DIR, exist_ok=True)

# Palabras clave por categoría 
topics = {
    "economia": ["economía", "económico", "colcap", "bvc", "inflación", "dólar", "tasas"],
    "seguridad": ["sicario", "asesinato", "homicidio", "violencia", "incidente", "capturado"],
    "politica": ["gobierno", "ministro", "presidente", "congreso", "alcalde", "elecciones"],
    "salud": ["salud", "hospital", "covid", "enfermedad", "clínica"],
}

def analyze_news():
    daily_counts = {}

    for path in glob.glob(os.path.join(CLEAN_DIR, "*.json")):
        with open(path, "r", encoding="utf-8") as f:
            doc = json.load(f)

        text = (doc.get("title", "") + " " + doc.get("text", "")).lower()

        # Fecha de la noticia
        date = doc.get("publish_date")
        if not date:
            date = datetime.utcnow().isoformat()

        day = date.split("T")[0]

        if day not in daily_counts:
            daily_counts[day] = collections.Counter()

        for topic, words in topics.items():
            if any(word in text for word in words):
                daily_counts[day][topic] += 1

    # Convertir a dataframe / json
    with open(os.path.join(OUT_DIR, "daily_counts.json"), "w", encoding="utf-8") as f:
        json.dump(daily_counts, f, ensure_ascii=False, indent=2)

    print("Archivo generado en:", os.path.join(OUT_DIR, "daily_counts.json"))

if __name__ == "__main__":
    analyze_news()
