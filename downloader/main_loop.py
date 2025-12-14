import feedparser
import json
import os
import time
from datetime import datetime

OUTDIR = "/app/data/raw"
os.makedirs(OUTDIR, exist_ok=True)

RSS_FEEDS = [
    "https://www.eltiempo.com/rss/colombia.xml",
    "https://www.portafolio.co/rss.xml",
    "https://www.elespectador.com/rss/economia",
]

def fetch_rss():
    """Descarga noticias de feeds RSS"""
    print(f"[{datetime.now()}] Iniciando descarga de noticias...")
    
    total = 0
    for url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            print(f"  - {url}: {len(feed.entries)} entradas")
            
            for entry in feed.entries:
                item = {
                    "title": entry.get("title", ""),
                    "link": entry.get("link", ""),
                    "summary": entry.get("summary", ""),
                    "published": entry.get("published", datetime.utcnow().isoformat()),
                    "source": url
                }
                
                # Usar hash del link para evitar duplicados
                import hashlib
                link_hash = hashlib.md5(item["link"].encode()).hexdigest()
                fname = os.path.join(OUTDIR, f"rss_{link_hash}.json")
                
                # Solo guardar si no existe
                if not os.path.exists(fname):
                    with open(fname, "w", encoding="utf-8") as f:
                        json.dump(item, f, ensure_ascii=False, indent=2)
                    total += 1
                    
        except Exception as e:
            print(f"  ❌ Error en {url}: {e}")
    
    print(f"✅ Descargadas {total} noticias nuevas\n")

def main():
    """Loop principal que ejecuta cada cierto tiempo"""
    interval = int(os.getenv("SLEEP_INTERVAL", 3600))
    
    while True:
        try:
            fetch_rss()
        except Exception as e:
            print(f"❌ Error en ciclo: {e}")
        
        print(f"💤 Esperando {interval} segundos...\n")
        time.sleep(interval)

if __name__ == "__main__":
    main()