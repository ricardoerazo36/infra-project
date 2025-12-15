import os
import json
import gzip
import time
import requests
from datetime import datetime
import hashlib

OUT_DIR = "/app/data/commoncrawl"
RAW_DIR = "/app/data/raw"
os.makedirs(OUT_DIR, exist_ok=True)

TARGET_DOMAINS = [
    "eltiempo.com",
    "portafolio.co",
    "elespectador.com",
    "semana.com",
    "larepublica.co"
]

class CommonCrawlFetcher:
    BASE_URL = "https://index.commoncrawl.org"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'NewsAnalyzer/1.0 (Educational)'
        })
    
    def get_indexes(self):
        try:
            url = f"{self.BASE_URL}/collinfo.json"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            indexes = response.json()
            print(f"✅ Encontrados {len(indexes)} índices")
            return indexes[:6]  # Últimos 6 meses
        except Exception as e:
            print(f"❌ Error: {e}")
            return []
    
    def search_domain(self, index_name, domain, limit=20):
        try:
            url = f"{self.BASE_URL}/{index_name}-index"
            params = {'url': domain, 'output': 'json', 'limit': limit}
            
            print(f"🔍 Buscando {domain} en {index_name}...")
            response = self.session.get(url, params=params, timeout=60)
            response.raise_for_status()
            
            results = []
            for line in response.text.strip().split('\n'):
                if line:
                    try:
                        results.append(json.loads(line))
                    except:
                        continue
            
            print(f"✅ {len(results)} URLs encontradas")
            return results
        except Exception as e:
            print(f"❌ Error: {e}")
            return []
    
    def download_warc(self, warc_record):
        try:
            filename = warc_record['filename']
            offset = int(warc_record['offset'])
            length = int(warc_record['length'])
            
            url = f"https://data.commoncrawl.org/{filename}"
            headers = {'Range': f'bytes={offset}-{offset+length-1}'}
            
            response = self.session.get(url, headers=headers, timeout=120)
            response.raise_for_status()
            
            return gzip.decompress(response.content).decode('utf-8', errors='ignore')
        except Exception as e:
            print(f"⚠️ Error descargando: {e}")
            return None
    
    def extract_article(self, warc_content, url):
        try:
            import re
            from html import unescape
            
            parts = warc_content.split('\r\n\r\n', 2)
            if len(parts) < 3:
                return None
            
            html = parts[2]
            
            title_match = re.search(r'<title[^>]*>(.*?)</title>', html, re.I | re.S)
            title = unescape(title_match.group(1)) if title_match else ""
            
            paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', html, re.I | re.S)
            text = ' '.join([unescape(re.sub(r'<[^>]+>', '', p)) for p in paragraphs])
            
            if len(text) < 100:
                return None
            
            return {'title': title.strip(), 'text': text.strip()[:3000], 'url': url}
        except Exception as e:
            return None

def fetch_news():
    print(f"\n{'='*60}")
    print(f"🚀 Iniciando recolección Common Crawl")
    print(f"{'='*60}\n")
    
    fetcher = CommonCrawlFetcher()
    indexes = fetcher.get_indexes()
    
    if not indexes:
        print("❌ No hay índices disponibles")
        return
    
    total = 0
    
    for index_info in indexes[:2]:  # Solo 2 índices para empezar
        index_name = index_info['id']
        print(f"\n📦 Procesando: {index_name}")
        
        for domain in TARGET_DOMAINS:
            results = fetcher.search_domain(index_name, domain, limit=10)
            
            for i, result in enumerate(results[:5]):  # 5 por dominio
                try:
                    url = result.get('url', '')
                    url_hash = hashlib.md5(url.encode()).hexdigest()
                    output_file = os.path.join(OUT_DIR, f"cc_{url_hash}.json")
                    
                    if os.path.exists(output_file):
                        continue
                    
                    print(f"  [{i+1}/5] Descargando...")
                    
                    warc_content = fetcher.download_warc(result)
                    if not warc_content:
                        continue
                    
                    article = fetcher.extract_article(warc_content, url)
                    if article:
                        data = {
                            'title': article['title'],
                            'text': article['text'],
                            'url': url,
                            'domain': domain,
                            'crawl_index': index_name,
                            'timestamp': result.get('timestamp', ''),
                            'fetched_at': datetime.now().isoformat(),
                            'source': 'common_crawl'
                        }
                        
                        with open(output_file, 'w', encoding='utf-8') as f:
                            json.dump(data, f, ensure_ascii=False, indent=2)
                        
                        total += 1
                        print(f"  ✅ {article['title'][:50]}...")
                    
                    time.sleep(2)
                except Exception as e:
                    print(f"  ⚠️ Error: {e}")
        
        print(f"\n📊 Total: {total} artículos")
    
    # Sincronizar al pipeline
    sync_to_pipeline()
    
    print(f"\n{'='*60}")
    print(f"✅ Completado: {total} artículos")
    print(f"{'='*60}\n")

def sync_to_pipeline():
    """Copia a data/raw para procesamiento"""
    cc_files = [f for f in os.listdir(OUT_DIR) 
                if f.startswith('cc_') and f.endswith('.json')]
    
    copied = 0
    for filename in cc_files:
        cc_path = os.path.join(OUT_DIR, filename)
        raw_path = os.path.join(RAW_DIR, filename)
        
        if not os.path.exists(raw_path):
            try:
                with open(cc_path, 'r', encoding='utf-8') as f:
                    cc_data = json.load(f)
                
                raw_data = {
                    "title": cc_data.get("title", ""),
                    "link": cc_data.get("url", ""),
                    "summary": cc_data.get("text", "")[:500],
                    "published": cc_data.get("timestamp", datetime.now().isoformat()),
                    "source": f"common_crawl:{cc_data.get('domain', '')}"
                }
                
                with open(raw_path, 'w', encoding='utf-8') as f:
                    json.dump(raw_data, f, ensure_ascii=False, indent=2)
                
                copied += 1
            except:
                pass
    
    if copied > 0:
        print(f"✅ Sincronizados {copied} artículos al pipeline")

def main():
    interval = int(os.getenv("SLEEP_INTERVAL", 86400))
    print(f"🚀 Common Crawl iniciado (cada {interval/3600:.1f}h)")
    
    while True:
        try:
            fetch_news()
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
        
        print(f"\n💤 Esperando {interval/3600:.1f} horas...\n")
        time.sleep(interval)

if __name__ == "__main__":
    main()