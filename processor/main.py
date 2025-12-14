import os
import json
from newspaper import Article
from bs4 import BeautifulSoup
from datetime import datetime

RAW_DIR = "/app/data/raw"
OUT_DIR = "/app/data/clean"

os.makedirs(OUT_DIR, exist_ok=True)


def extract_from_html(html):
    """
    Extrae texto limpio desde HTML usando newspaper3k o BeautifulSoup como fallback.
    """
    try:
        article = Article("")
        article.set_html(html)
        article.parse()
        if article.text.strip():
            return article.text
    except:
        pass

    # Fallback: usar BeautifulSoup si newspaper falla
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text(separator="\n", strip=True)


def process_file(path):
    print(f"Procesando: {path}")

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Detectar HTML disponible
    html = ""

    # 1️⃣ Caso RSS → tiene "summary"
    if "summary" in data and data["summary"]:
        html = data["summary"]

    # 2️⃣ Caso Common Crawl → tiene "html"
    elif "html" in data:
        html = data["html"]

    # 3️⃣ Si el HTML viene anidado
    elif "content" in data:
        html = str(data["content"])

    else:
        print("❌ No se encontró campo HTML útil")
        return

    text = extract_from_html(html)

    # Crear JSON limpio
    cleaned = {
        "title": data.get("title", "sin_titulo"),
        "url": data.get("link", ""),
        "text": text,
        "timestamp": datetime.now().isoformat()
    }

    outname = os.path.basename(path).replace(".json", "_clean.json")
    outpath = os.path.join(OUT_DIR, outname)

    with open(outpath, "w", encoding="utf-8") as f:
        json.dump(cleaned, f, ensure_ascii=False)

    print(f"✔ Guardado: {outpath}")


def main():
    files = [f for f in os.listdir(RAW_DIR) if f.endswith(".json")]

    if not files:
        print("No hay archivos en data/raw")
        return

    for file in files:
        process_file(os.path.join(RAW_DIR, file))


if __name__ == "__main__":
    main()
