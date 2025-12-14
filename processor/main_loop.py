import os
import json
import time
import re
from datetime import datetime
from html import unescape

RAW_DIR = "/app/data/raw"
CLEAN_DIR = "/app/data/clean"

os.makedirs(CLEAN_DIR, exist_ok=True)

def clean_html(text):
    """Elimina etiquetas HTML y limpia el texto"""
    if not text:
        return ""
    
    # Decodificar entidades HTML
    text = unescape(text)
    
    # Eliminar etiquetas HTML
    text = re.sub(r'<[^>]+>', '', text)
    
    # Eliminar múltiples espacios
    text = re.sub(r'\s+', ' ', text)
    
    # Eliminar caracteres especiales problemáticos
    text = text.replace('\xa0', ' ')
    text = text.replace('\u200b', '')
    
    return text.strip()

def extract_date(published_str):
    """
    Extrae y normaliza la fecha de publicación
    Maneja diferentes formatos de fecha
    """
    if not published_str:
        return datetime.utcnow().isoformat()
    
    try:
        # Intentar parsear diferentes formatos comunes
        from dateutil import parser
        dt = parser.parse(published_str)
        return dt.isoformat()
    except:
        # Si falla, usar fecha actual
        return datetime.utcnow().isoformat()

def process_article(raw_data):
    """Procesa un artículo individual"""
    try:
        # Limpiar título
        title = clean_html(raw_data.get("title", ""))
        
        # Limpiar resumen/contenido
        summary = clean_html(raw_data.get("summary", ""))
        
        # Extraer fecha
        publish_date = extract_date(raw_data.get("published"))
        
        # Estructura limpia
        clean_data = {
            "title": title,
            "text": summary,
            "publish_date": publish_date,
            "source": raw_data.get("source", "unknown"),
            "link": raw_data.get("link", ""),
            "processed_at": datetime.now().isoformat()
        }
        
        # Validar que tenga contenido mínimo
        if len(title) < 10 and len(summary) < 20:
            return None
        
        return clean_data
        
    except Exception as e:
        print(f"  ⚠️  Error procesando artículo: {e}")
        return None

def process_all_files():
    """Procesa todos los archivos en el directorio raw"""
    print(f"[{datetime.now()}] Iniciando procesamiento de noticias...")
    
    processed = 0
    skipped = 0
    
    # Obtener lista de archivos raw
    raw_files = [f for f in os.listdir(RAW_DIR) if f.endswith('.json')]
    
    print(f"📄 Archivos encontrados: {len(raw_files)}")
    
    for filename in raw_files:
        raw_path = os.path.join(RAW_DIR, filename)
        
        # Usar mismo nombre para archivo limpio
        clean_path = os.path.join(CLEAN_DIR, filename)
        
        # Saltar si ya fue procesado
        if os.path.exists(clean_path):
            skipped += 1
            continue
        
        try:
            # Leer archivo raw
            with open(raw_path, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)
            
            # Procesar
            clean_data = process_article(raw_data)
            
            if clean_data:
                # Guardar archivo limpio
                with open(clean_path, 'w', encoding='utf-8') as f:
                    json.dump(clean_data, f, ensure_ascii=False, indent=2)
                
                processed += 1
            else:
                skipped += 1
                
        except Exception as e:
            print(f"  ❌ Error con {filename}: {e}")
            skipped += 1
    
    print(f"✅ Procesados: {processed} nuevos")
    print(f"⏭️  Saltados: {skipped} (ya procesados o inválidos)\n")

def cleanup_old_files(days_to_keep=7):
    """
    Limpia archivos antiguos para ahorrar espacio
    Mantiene solo los últimos N días
    """
    from datetime import timedelta
    
    cutoff_date = datetime.now() - timedelta(days=days_to_keep)
    
    deleted = 0
    
    for directory in [RAW_DIR, CLEAN_DIR]:
        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            
            # Obtener fecha de modificación
            file_mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
            
            # Eliminar si es muy antiguo
            if file_mtime < cutoff_date:
                os.remove(filepath)
                deleted += 1
    
    if deleted > 0:
        print(f"🗑️  Eliminados {deleted} archivos antiguos")

def get_statistics():
    """Obtiene estadísticas del procesamiento"""
    raw_count = len([f for f in os.listdir(RAW_DIR) if f.endswith('.json')])
    clean_count = len([f for f in os.listdir(CLEAN_DIR) if f.endswith('.json')])
    
    return {
        "raw_files": raw_count,
        "clean_files": clean_count,
        "pending": raw_count - clean_count
    }

def main():
    """Loop principal del procesador"""
    interval = int(os.getenv("SLEEP_INTERVAL", 1800))
    
    print("🚀 Iniciando procesador de noticias...")
    print(f"⏱️  Intervalo: {interval} segundos ({interval/60:.1f} minutos)\n")
    
    while True:
        try:
            # Mostrar estadísticas
            stats = get_statistics()
            print(f"📊 Estado: {stats['clean_files']} procesados, "
                  f"{stats['pending']} pendientes")
            
            # Procesar archivos nuevos
            process_all_files()
            
            # Limpiar archivos antiguos (ejecutar cada 10 ciclos)
            if int(time.time()) % (interval * 10) < interval:
                cleanup_old_files()
            
        except Exception as e:
            print(f"❌ Error en ciclo principal: {e}")
            import traceback
            traceback.print_exc()
        
        print(f"💤 Esperando {interval} segundos...\n")
        time.sleep(interval)

if __name__ == "__main__":
    main()