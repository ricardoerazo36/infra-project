import os
import json
import shutil
from datetime import datetime

CC_DIR = "/app/data/commoncrawl"
RAW_DIR = "/app/data/raw"

def sync_commoncrawl_to_pipeline():
    """
    Copia artículos de Common Crawl al directorio raw
    para que el pipeline existente los procese
    """
    cc_files = [f for f in os.listdir(CC_DIR) 
                if f.startswith('cc_') and f.endswith('.json')]
    
    copied = 0
    
    for filename in cc_files:
        cc_path = os.path.join(CC_DIR, filename)
        raw_path = os.path.join(RAW_DIR, filename)
        
        # Solo copiar si no existe en raw
        if not os.path.exists(raw_path):
            try:
                # Leer datos de Common Crawl
                with open(cc_path, 'r', encoding='utf-8') as f:
                    cc_data = json.load(f)
                
                # Adaptar formato para pipeline existente
                raw_data = {
                    "title": cc_data.get("title", ""),
                    "link": cc_data.get("url", ""),
                    "summary": cc_data.get("text", "")[:500],  # Resumen
                    "published": cc_data.get("timestamp", datetime.now().isoformat()),
                    "source": f"common_crawl:{cc_data.get('domain', '')}"
                }
                
                # Guardar en formato del pipeline
                with open(raw_path, 'w', encoding='utf-8') as f:
                    json.dump(raw_data, f, ensure_ascii=False, indent=2)
                
                copied += 1
                
            except Exception as e:
                print(f"Error copiando {filename}: {e}")
    
    if copied > 0:
        print(f"✅ Sincronizados {copied} artículos de Common Crawl al pipeline")

if __name__ == "__main__":
    import time
    while True:
        sync_commoncrawl_to_pipeline()
        time.sleep(3600)  # Cada hora