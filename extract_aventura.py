import requests
import json
import re
import time
from concurrent.futures import ThreadPoolExecutor

SLUG = "aventura-prohibida-con-el-papa-de-mi-mejor-amiga-doblado"
TOTAL_EPS = 51

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Referer': 'https://narto-drama.com/'
}

def fetch_ep(ep_num):
    url = f"https://narto-drama.com/detail/watch/{SLUG}/{ep_num}?lang=es-ES"
    for attempt in range(3):
        try:
            r = requests.get(url, headers=headers, timeout=12)
            if r.status_code == 200:
                m = re.search(r'"contentUrl"\s*:\s*"([^"]+)"', r.text)
                if m:
                    return ep_num, m.group(1)
        except Exception:
            time.sleep(0.5)
    return ep_num, None

print(f"Extracting all {TOTAL_EPS} episodes for '{SLUG}'...")
episodes = {}
with ThreadPoolExecutor(max_workers=8) as executor:
    results = executor.map(fetch_ep, range(1, TOTAL_EPS + 1))
    for ep, vurl in results:
        if vurl:
            episodes[str(ep)] = vurl
            print(f"  [OK] Ep {ep}/{TOTAL_EPS}")
        else:
            print(f"  [ERR] Ep {ep}/{TOTAL_EPS} missing")

item = {
    "slug": f"nt-{SLUG}",
    "title": "Aventura prohibida con el papá de mi mejor amiga (Doblado)",
    "description": "Tras descubrir en el vuelo que su prometido le es infiel, Mía queda destrozada. Está rumbo a la boda de su mejor amiga. Borracha y dolida, se siente profundamente atraída por Damián, un atractivo multimillonario mayor. Pero pronto descubre que es el padre de su amiga. Durante el caótico fin de semana, deberán mantener en secreto su aventura prohibida, mientras enfrentan la venganza de sus ex celosos, el riesgo de arruinar la boda y destruir la amistad.",
    "poster": "https://img.nartodrama-api.online/poster/762309.jpg",
    "section": "hotdrama",
    "source": "narto",
    "total_episodes": len(episodes),
    "genres": ["CEO", "Sentimientos ocultos", "Diferencia de edad", "Amor prohibido", "Doblado"],
    "episodes": episodes
}

with open('_extracted_aventura.json', 'w', encoding='utf-8') as f:
    json.dump(item, f, indent=2, ensure_ascii=False)

print(f"\nExtraction complete! Total episodes extracted: {len(episodes)}/{TOTAL_EPS}")
