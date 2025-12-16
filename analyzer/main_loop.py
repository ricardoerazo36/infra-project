import os
import json
import glob
import time
import collections
import pandas as pd
from datetime import datetime

CLEAN_DIR = "/app/data/clean"
OUT_DIR = "/app/data/analysis"

os.makedirs(OUT_DIR, exist_ok=True)

# Palabras clave por categoría 
topics = {
    "economia": ["economía", "económico", "colcap", "bvc", "inflación", "dólar", "tasas"],
    "seguridad": ["sicario", "asesinato", "homicidio", "violencia", "incidente", "capturado", "paro armado", "eln", "ataque", "explosión"],
    "politica": ["gobierno", "ministro", "presidente", "congreso", "alcalde", "elecciones", "política"],
    "salud": ["salud", "hospital", "covid", "enfermedad", "clínica", "medicina"],
}

def analyze_news():
    """Analiza noticias y cuenta por categoría"""
    print(f"[{datetime.now()}] Iniciando análisis de noticias...")
    
    daily_counts = {}
    total_analyzed = 0

    # Buscar todos los archivos JSON en clean
    clean_files = glob.glob(os.path.join(CLEAN_DIR, "*.json"))
    
    print(f"📄 Archivos a analizar: {len(clean_files)}")

    for path in clean_files:
        try:
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

            # Contar por cada tema
            for topic, words in topics.items():
                if any(word in text for word in words):
                    daily_counts[day][topic] += 1
            
            total_analyzed += 1
            
        except Exception as e:
            print(f"  ⚠️ Error procesando {path}: {e}")

    # Convertir Counter a dict normal para JSON
    daily_counts_serializable = {}
    for day, counter in daily_counts.items():
        daily_counts_serializable[day] = dict(counter)

    # Guardar resultado
    output_file = os.path.join(OUT_DIR, "daily_counts.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(daily_counts_serializable, f, ensure_ascii=False, indent=2)

    print(f"✅ Análisis completado:")
    print(f"   - Archivos analizados: {total_analyzed}")
    print(f"   - Días con datos: {len(daily_counts)}")
    print(f"   - Archivo generado: {output_file}")
    
    # Mostrar resumen
    if daily_counts:
        print(f"\n📊 Resumen por día:")
        for day in sorted(daily_counts.keys())[-3:]:  # Últimos 3 días
            counts = daily_counts[day]
            print(f"   {day}: {dict(counts)}")
    
    return len(daily_counts)

def main():
    """Loop principal del analizador"""
    interval = int(os.getenv("SLEEP_INTERVAL", 1800))
    
    print("🚀 Iniciando analizador de noticias...")
    print(f"⏱️  Intervalo: {interval} segundos ({interval/60:.1f} minutos)\n")
    
    while True:
        try:
            days_analyzed = analyze_news()
            
            if days_analyzed == 0:
                print("⚠️  No hay datos para analizar aún")
            
        except Exception as e:
            print(f"❌ Error en ciclo principal: {e}")
            import traceback
            traceback.print_exc()
        
        print(f"\n💤 Esperando {interval} segundos...\n")
        time.sleep(interval)

if __name__ == "__main__":
    main()