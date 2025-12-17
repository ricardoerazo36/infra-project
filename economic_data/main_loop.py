import os
import json
import time
import requests
from datetime import datetime

OUT_DIR = "/app/data/economic"
os.makedirs(OUT_DIR, exist_ok=True)

# Configuración de Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyD6ack4EEr-ovTW9VTVSJfdkdrElcJf89o")
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"


def get_colcap_from_gemini():
    """
    Usa Gemini para obtener el valor actual del COLCAP
    Gemini puede buscar en internet información actualizada
    """
    if not GEMINI_API_KEY:
        print("⚠️ GEMINI_API_KEY no configurada, usando valor por defecto")
        return None
    
    try:
        headers = {
            "Content-Type": "application/json"
        }
        
        # Prompt específico para obtener solo el número
        prompt = """Busca el valor actual del índice COLCAP de la Bolsa de Valores de Colombia.
        
        Responde ÚNICAMENTE con un JSON en este formato exacto, sin explicaciones adicionales:
        {"colcap": 1234.56, "fecha": "2025-12-17", "fuente": "nombre de la fuente"}
        
        Si no puedes encontrar el valor exacto, responde:
        {"colcap": null, "error": "razón"}"""
        
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": 0.1,  # Baja temperatura para respuestas más precisas
                "maxOutputTokens": 200
            }
        }
        
        response = requests.post(
            f"{GEMINI_URL}?key={GEMINI_API_KEY}",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        response.raise_for_status()
        data = response.json()
        
        # Extraer el texto de la respuesta
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        print(f"📡 Respuesta de Gemini: {text}")
        
        # Limpiar el texto (a veces viene con ```json ... ```)
        text = text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        text = text.strip()
        
        # Parsear JSON
        result = json.loads(text)
        
        if result.get("colcap"):
            print(f"✅ COLCAP obtenido: {result['colcap']} (Fuente: {result.get('fuente', 'Gemini')})")
            return float(result["colcap"])
        else:
            print(f"⚠️ Gemini no pudo obtener el valor: {result.get('error')}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión con Gemini: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Error parseando respuesta de Gemini: {e}")
        return None
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return None


def get_usd_cop_from_gemini():
    """
    Usa Gemini para obtener la tasa de cambio USD/COP
    """
    if not GEMINI_API_KEY:
        return None
    
    try:
        headers = {"Content-Type": "application/json"}
        
        prompt = """Busca la tasa de cambio actual del dólar estadounidense a peso colombiano (USD/COP).
        
        Responde ÚNICAMENTE con un JSON en este formato exacto:
        {"usd_cop": 4150.25, "fecha": "2025-12-17"}
        
        Si no puedes encontrar el valor, responde:
        {"usd_cop": null, "error": "razón"}"""
        
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.1, "maxOutputTokens": 150}
        }
        
        response = requests.post(
            f"{GEMINI_URL}?key={GEMINI_API_KEY}",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        response.raise_for_status()
        data = response.json()
        text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
        
        # Limpiar markdown si existe
        if "```" in text:
            text = text.split("```")[1].replace("json", "").strip()
        
        result = json.loads(text)
        
        if result.get("usd_cop"):
            print(f"✅ USD/COP obtenido: {result['usd_cop']}")
            return float(result["usd_cop"])
        return None
        
    except Exception as e:
        print(f"❌ Error obteniendo USD/COP: {e}")
        return None


def get_fallback_value():
    """
    Valor de respaldo si Gemini no está disponible
    Usa el último valor conocido o un valor por defecto
    """
    historical_file = os.path.join(OUT_DIR, "colcap_historical.json")
    
    if os.path.exists(historical_file):
        try:
            with open(historical_file, "r") as f:
                historical = json.load(f)
            if historical:
                last_value = historical[-1]["value"]
                print(f"📂 Usando último valor conocido: {last_value}")
                return last_value
        except:
            pass
    
    # Valor por defecto aproximado del COLCAP
    print("📌 Usando valor por defecto: 1450.00")
    return 1450.00


def fetch_colcap_data():
    """
    Obtiene datos del COLCAP, primero intenta con Gemini,
    si falla usa el valor de respaldo
    """
    print(f"\n[{datetime.now()}] Obteniendo datos del COLCAP...")
    
    # Intentar obtener de Gemini
    colcap_value = get_colcap_from_gemini()
    
    # Si Gemini falla, usar fallback
    if colcap_value is None:
        colcap_value = get_fallback_value()
        source = "fallback"
    else:
        source = "gemini"
    
    today = datetime.now().date()
    
    data_point = {
        "date": today.isoformat(),
        "index": "COLCAP",
        "value": colcap_value,
        "source": source,
        "timestamp": datetime.now().isoformat()
    }
    
    # Guardar datos diarios
    filename = os.path.join(OUT_DIR, f"colcap_{today.isoformat()}.json")
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data_point, f, ensure_ascii=False, indent=2)
    
    print(f"💾 Datos guardados: {filename}")
    
    # Actualizar histórico
    update_historical_data(data_point)
    
    return colcap_value


def update_historical_data(new_data):
    """Actualiza el archivo histórico con los nuevos datos"""
    historical_file = os.path.join(OUT_DIR, "colcap_historical.json")
    
    if os.path.exists(historical_file):
        with open(historical_file, "r", encoding="utf-8") as f:
            historical = json.load(f)
    else:
        historical = []
    
    # Actualizar o agregar dato para la fecha
    date_exists = False
    for i, item in enumerate(historical):
        if item["date"] == new_data["date"]:
            historical[i] = new_data
            date_exists = True
            break
    
    if not date_exists:
        historical.append(new_data)
    
    # Ordenar por fecha
    historical.sort(key=lambda x: x["date"])
    
    # Guardar
    with open(historical_file, "w", encoding="utf-8") as f:
        json.dump(historical, f, ensure_ascii=False, indent=2)
    
    print(f"📊 Histórico actualizado: {len(historical)} registros")


def fetch_additional_economic_data():
    """Obtiene datos económicos adicionales (USD/COP)"""
    print(f"[{datetime.now()}] Obteniendo datos económicos adicionales...")
    
    today = datetime.now().date()
    
    # Intentar obtener USD/COP de Gemini
    usd_cop = get_usd_cop_from_gemini()
    
    if usd_cop is None:
        # Fallback: valor aproximado
        usd_cop = 4150.00
        print(f"📌 USD/COP usando valor por defecto: {usd_cop}")
    
    economic_data = {
        "date": today.isoformat(),
        "usd_cop": usd_cop,
        "timestamp": datetime.now().isoformat()
    }
    
    filename = os.path.join(OUT_DIR, f"economic_{today.isoformat()}.json")
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(economic_data, f, ensure_ascii=False, indent=2)
    
    print(f"💾 Datos económicos guardados: {filename}")


def main():
    """Loop principal"""
    interval = int(os.getenv("SLEEP_INTERVAL", 3600))
    
    print("=" * 60)
    print("🚀 RECOLECTOR DE DATOS ECONÓMICOS")
    print("=" * 60)
    print(f"⏱️  Intervalo: {interval} segundos ({interval/3600:.1f} horas)")
    print(f"🔑 Gemini API: {'✅ Configurada' if GEMINI_API_KEY else '❌ No configurada'}")
    print("=" * 60)
    
    while True:
        try:
            fetch_colcap_data()
            fetch_additional_economic_data()
        except Exception as e:
            print(f"❌ Error en ciclo principal: {e}")
            import traceback
            traceback.print_exc()
        
        print(f"\n💤 Esperando {interval} segundos...\n")
        time.sleep(interval)


if __name__ == "__main__":
    main()