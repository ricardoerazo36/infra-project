import requests
from warcio.archiveiterator import ArchiveIterator
import json
import os
from datetime import datetime

OUTDIR = "../data/raw"
os.makedirs(OUTDIR, exist_ok=True)

# Dominio a descargar
DOMAIN = "eltiempo.com"

# Cantidad de documentos que quieres bajar
LIMIT = 5

def fetch_index(domain):
    print("Buscando entradas en Common Crawl…")

    url = f"https://index.commoncrawl.org/CC-MAIN-2023-40-index?url={domain}/*&output=json"

    r = requests.get(url)

    all_entries = [json.loads(line) for line in r.text.splitlines()]

    print(f"Total encontradas: {len(all_entries)}")

    # Filtrar páginas HTML útiles (filtro amplio)
    filtered = []
    for e in all_entries:
        u = e["url"].lower()

        # Archivos inútiles
        if any(u.endswith(ext) for ext in [
            ".txt", ".jpg", ".png", ".gif", ".jpeg", ".pdf", ".css", ".js", ".svg",
            ".mp4", ".webp", ".ico"
        ]):
            continue

        if "robots.txt" in u:
            continue

        # Aceptar solo URLs con estructura de artículo (mínimo 4 slashes)
        if u.count("/") < 4:
            continue

        filtered.append(e)

    print(f"Filtradas (válidas): {len(filtered)}")

    return filtered[:LIMIT]



def download(entry):
    warc = entry["filename"]

    #  Convertir offset y length a números
    offset = int(entry["offset"])
    length = int(entry["length"])

    warc_url = f"https://data.commoncrawl.org/{warc}"

    headers = {"Range": f"bytes={offset}-{offset + length - 1}"}

    print(f"\nDescargando: {entry['url']}")

    r = requests.get(warc_url, headers=headers, stream=True)

    for record in ArchiveIterator(r.raw):
        if record.rec_type == "response":
            html = record.content_stream().read().decode("utf-8", errors="ignore")

            out = {
                "title": entry["url"],
                "link": entry["url"],
                "html": html,
                "timestamp": datetime.utcnow().isoformat()
            }

            fname = os.path.join(OUTDIR, f"cc_{int(datetime.utcnow().timestamp()*1000)}.json")
            with open(fname, "w", encoding="utf-8") as f:
                json.dump(out, f, ensure_ascii=False)

            print("Guardado:", fname)
            return


def main():
    entries = fetch_index(DOMAIN)

    if not entries:
        print("No se encontraron páginas HTML válidas.")
        return

    for e in entries:
        download(e)

if __name__ == "__main__":
    main()
