import os
import json
import time
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict

ANALYSIS_DIR = "/app/data/analysis"
ECONOMIC_DIR = "/app/data/economic"
RESULTS_DIR = "/app/data/results"

os.makedirs(RESULTS_DIR, exist_ok=True)

def load_news_data():
    """Carga los conteos diarios de noticias por tema"""
    daily_counts_file = os.path.join(ANALYSIS_DIR, "daily_counts.json")
    
    if not os.path.exists(daily_counts_file):
        print("⚠️  No hay datos de noticias disponibles")
        return {}
    
    with open(daily_counts_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    print(f"✅ Cargados datos de noticias: {len(data)} días")
    return data

def load_colcap_data():
    """Carga los datos históricos del COLCAP"""
    historical_file = os.path.join(ECONOMIC_DIR, "colcap_historical.json")
    
    if not os.path.exists(historical_file):
        print("⚠️  No hay datos del COLCAP disponibles")
        return {}
    
    with open(historical_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Convertir a diccionario por fecha
    colcap_by_date = {item["date"]: item["value"] for item in data}
    
    print(f"✅ Cargados datos COLCAP: {len(colcap_by_date)} días")
    return colcap_by_date

def calculate_correlations(news_data, colcap_data):
    """
    Calcula correlaciones entre temas de noticias y variación del COLCAP
    """
    print(f"[{datetime.now()}] Calculando correlaciones...")
    
    # Obtener fechas comunes
    news_dates = set(news_data.keys())
    colcap_dates = set(colcap_data.keys())
    common_dates = sorted(news_dates & colcap_dates)
    
    if len(common_dates) < 2:
        print("⚠️  Insuficientes datos para correlación")
        return {}, []
    
    print(f"📊 Analizando {len(common_dates)} días comunes")
    
    # Preparar series de tiempo
    topics = ["economia", "seguridad", "politica", "salud"]
    
    # Calcular variación porcentual del COLCAP
    colcap_changes = []
    valid_dates = []
    
    for i in range(1, len(common_dates)):
        prev_date = common_dates[i-1]
        curr_date = common_dates[i]
        
        prev_value = colcap_data[prev_date]
        curr_value = colcap_data[curr_date]
        
        if prev_value > 0:
            change_pct = ((curr_value - prev_value) / prev_value) * 100
            colcap_changes.append(change_pct)
            valid_dates.append(curr_date)
    
    # Calcular correlaciones por tema
    correlations = {}
    
    for topic in topics:
        topic_counts = []
        
        for date in valid_dates:
            count = news_data.get(date, {}).get(topic, 0)
            topic_counts.append(count)
        
        # Calcular correlación de Pearson
        if len(topic_counts) > 1 and len(colcap_changes) > 1:
            correlation = np.corrcoef(topic_counts, colcap_changes)[0, 1]
            
            # Manejar NaN (cuando no hay variación)
            if np.isnan(correlation):
                correlation = 0.0
            
            correlations[topic] = float(correlation)
    
    # Generar insights
    insights = generate_insights(correlations, news_data, colcap_data, valid_dates)
    
    return correlations, insights

def generate_insights(correlations, news_data, colcap_data, dates):
    """Genera insights interpretables de las correlaciones"""
    insights = []
    
    for topic, corr in correlations.items():
        if abs(corr) > 0.3:  # Correlación significativa
            direction = "positiva" if corr > 0 else "negativa"
            strength = "fuerte" if abs(corr) > 0.7 else "moderada"
            
            insight_text = (
                f"Correlación {strength} {direction} ({corr:.3f}). "
                f"Las noticias de {topic} {'aumentan' if corr > 0 else 'disminuyen'} "
                f"cuando el COLCAP sube."
            )
            
            insights.append({
                "topic": topic,
                "correlation": corr,
                "insight": insight_text
            })
    
    # Insight sobre período
    if dates:
        avg_news = np.mean([sum(news_data.get(d, {}).values()) for d in dates])
        insights.append({
            "topic": "general",
            "insight": f"Promedio de {avg_news:.1f} noticias diarias en el período analizado."
        })
    
    return insights

def save_results(correlations, insights, dates):
    """Guarda los resultados del análisis"""
    results = {
        "timestamp": datetime.now().isoformat(),
        "correlations": correlations,
        "insights": insights,
        "period": {
            "start": dates[0] if dates else None,
            "end": dates[-1] if dates else None,
            "days": len(dates)
        }
    }
    
    # Guardar con timestamp
    timestamp_file = os.path.join(
        RESULTS_DIR, 
        f"correlations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    
    with open(timestamp_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    # Guardar versión "latest" para el dashboard
    latest_file = os.path.join(RESULTS_DIR, "correlations_latest.json")
    
    with open(latest_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Resultados guardados:")
    print(f"   - {timestamp_file}")
    print(f"   - {latest_file}")
    
    # Mostrar resumen
    print(f"\n📊 Resumen de correlaciones:")
    for topic, corr in correlations.items():
        emoji = "📈" if corr > 0 else "📉"
        print(f"   {emoji} {topic}: {corr:.3f}")

def cleanup_old_results(days_to_keep=30):
    """Limpia resultados antiguos para ahorrar espacio"""
    cutoff_date = datetime.now() - timedelta(days=days_to_keep)
    
    for filename in os.listdir(RESULTS_DIR):
        if filename.startswith("correlations_") and filename != "correlations_latest.json":
            filepath = os.path.join(RESULTS_DIR, filename)
            file_mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
            
            if file_mtime < cutoff_date:
                os.remove(filepath)
                print(f"🗑️  Eliminado: {filename}")

def main():
    """Loop principal del correlador"""
    interval = int(os.getenv("SLEEP_INTERVAL", 3600))
    
    print("🚀 Iniciando correlador de datos...")
    print(f"⏱️  Intervalo: {interval} segundos ({interval/3600:.1f} horas)\n")
    
    while True:
        try:
            # Cargar datos
            news_data = load_news_data()
            colcap_data = load_colcap_data()
            
            if not news_data or not colcap_data:
                print("⚠️  Esperando datos suficientes...")
            else:
                # Calcular correlaciones
                correlations, insights = calculate_correlations(news_data, colcap_data)
                
                # Guardar resultados
                if correlations:
                    dates = sorted(set(news_data.keys()) & set(colcap_data.keys()))
                    save_results(correlations, insights, dates)
                    
                    # Limpiar archivos antiguos
                    cleanup_old_results()
            
        except Exception as e:
            print(f"❌ Error en ciclo principal: {e}")
            import traceback
            traceback.print_exc()
        
        print(f"\n💤 Esperando {interval} segundos...\n")
        time.sleep(interval)

if __name__ == "__main__":
    main()