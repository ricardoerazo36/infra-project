import feedparser
import json
import os
from datetime import datetime

# Carpeta donde guardaremos las noticias descargadas
OUTDIR = "data/raw"   # usando ruta local para pruebas en Windows
os.makedirs(OUTDIR, exist_ok=True)

# URLs RSS de noticias 
RSS_FEEDS = [
    "https://www.eltiempo.com/rss/colombia.xml",
    "https://www.portafolio.co/rss.xml"
]

def fetch_rss():
    for url in RSS_FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            item = {
                "title": entry.get("title"),
                "link": entry.get("link"),
                "published": entry.get("published", datetime.utcnow().isoformat()),
            }
            timestamp = int(datetime.utcnow().timestamp() * 1000)
            fname = os.path.join(OUTDIR, f"{timestamp}.json")
            with open(fname, "w", encoding="utf-8") as f:
                json.dump(item, f, ensure_ascii=False)
            print("Saved", fname)

if __name__ == "__main__":
    fetch_rss()
