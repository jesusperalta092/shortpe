import json
import requests

with open('data/hotdrama.json', encoding='utf-8') as f:
    items = json.load(f)

narto_items = [d for d in items if d.get('source') == 'narto' or d.get('slug', '').startswith('nt-')]
print(f"Total narto items: {len(narto_items)}")

for d in narto_items:
    slug = d['slug']
    narto_slug = slug[3:] if slug.startswith('nt-') else slug
    url = f"https://edge.narto-drama.com/e/rs/detail/watch/{narto_slug}/1/refresh-source?force=1&lang=es-ES"
    try:
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0', 'Referer': 'https://narto-drama.com/'}, timeout=8)
        if r.status_code == 200 and r.json().get('ok'):
            data = r.json()
            play_url = data.get('play_url') or data.get('direct_play_url')
            print(f"[OK] {slug}: {play_url[:60]}...")
        else:
            print(f"[FAIL {r.status_code}] {slug}: {r.text[:80]}")
    except Exception as e:
        print(f"[ERR] {slug}: {e}")
