import os
import json
import time
import requests
from datetime import datetime, timedelta

OUT_DIR = "/app/data/economic"
os.makedirs(OUT_DIR, exist_ok=True)

def fetch_colcap_data():
    """
    Descarga datos del índice COLCAP de la Bolsa de Valores de Colombia
    Nota: Esta es una implementación simulada. En producción necesitarías
    una API real o scraping de datos bursátiles.
    """
    print(f"[{datetime.now()}] Obteniendo datos del COLCAP...")
    
    try:
        # Ejemplo usando Yahoo Finance API (alternativa gratuita)
        # Para COLCAP real necesitarías acceso a BVC o Bloomberg
        
        # API de ejemplo - ajusta según tu fuente de datos
        # url = "https://query1.finance.yahoo.com/v8/finance/chart/^COLCAP"
        
        # Por ahora, generamos datos de ejemplo estructurados
        # En producción, reemplaza esto con una API real
        
        today = datetime.now().date()
        data_point = {
            "date": today.isoformat(),
            "index": "COLCAP",
            "value": get_mock_colcap_value(),  # Reemplazar con API real
            "timestamp": datetime.now().isoformat()
        }
        
        # Guardar datos diarios
        filename = os.path.join(OUT_DIR, f"colcap_{today.isoformat()}.json")
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data_point, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Datos guardados: {filename}")
        
        # Mantener histórico consolidado
        update_historical_data(data_point)
        
    except Exception as e:
        print(f"❌ Error obteniendo datos COLCAP: {e}")

def get_mock_colcap_value():
    """
    Genera valores simulados del COLCAP
    REEMPLAZAR con llamada a API real en producción
    """
    import random
    # Valor base aproximado del COLCAP (ajustar según datos reales)
    base_value = 1500
    variation = random.uniform(-20, 20)
    return round(base_value + variation, 2)

def update_historical_data(new_data):
    """Actualiza el archivo histórico con los nuevos datos"""
    historical_file = os.path.join(OUT_DIR, "colcap_historical.json")
    
    # Cargar histórico existente
    if os.path.exists(historical_file):
        with open(historical_file, "r", encoding="utf-8") as f:
            historical = json.load(f)
    else:
        historical = []
    
    # Agregar nuevo dato si no existe para esa fecha
    if not any(d["date"] == new_data["date"] for d in historical):
        historical.append(new_data)
    
    # Ordenar por fecha
    historical.sort(key=lambda x: x["date"])
    
    # Guardar actualizado
    with open(historical_file, "w", encoding="utf-8") as f:
        json.dump(historical, f, ensure_ascii=False, indent=2)

def fetch_additional_economic_data():
    """
    Obtiene datos económicos adicionales como:
    - Tasa de cambio USD/COP
    - Tasa de interés
    - Inflación
    """
    print(f"[{datetime.now()}] Obteniendo datos económicos adicionales...")
    
    try:
        today = datetime.now().date()
        
        economic_data = {
            "date": today.isoformat(),
            "usd_cop": get_exchange_rate(),  # Implementar con API real
            "timestamp": datetime.now().isoformat()
        }
        
        filename = os.path.join(OUT_DIR, f"economic_{today.isoformat()}.json")
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(economic_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Datos económicos guardados: {filename}")
        
    except Exception as e:
        print(f"❌ Error obteniendo datos económicos: {e}")

def get_exchange_rate():
    """
    Obtiene tasa de cambio USD/COP
    REEMPLAZAR con API real (ej: exchangerate-api.com, fixer.io)
    """
    try:
        # API de ejemplo gratuita para tasas de cambio
        # url = "https://api.exchangerate-api.com/v4/latest/USD"
        # response = requests.get(url, timeout=10)
        # data = response.json()
        # return data["rates"].get("COP", 4000)
        
        import random
        return round(4000 + random.uniform(-100, 100), 2)
    except:
        return 4000  # Valor por defecto

def main():
    """Loop principal que ejecuta cada cierto tiempo"""
    interval = int(os.getenv("SLEEP_INTERVAL", 3600))
    
    print("🚀 Iniciando recolector de datos económicos...")
    print(f"⏱️  Intervalo: {interval} segundos ({interval/3600:.1f} horas)")
    
    while True:
        try:
            fetch_colcap_data()
            fetch_additional_economic_data()
        except Exception as e:
            print(f"❌ Error en ciclo principal: {e}")
        
        print(f"💤 Esperando {interval} segundos...\n")
        time.sleep(interval)

if __name__ == "__main__":
    main()