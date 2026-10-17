import json, requests

with open('data/hotdrama.json', encoding='utf-8') as f:
    items = json.load(f)

narto_items = [d for d in items if d.get('source') == 'narto' or d.get('slug', '').startswith('nt-')]

working = []
broken = []

for d in narto_items:
    slug = d['slug']
    narto_slug = slug[3:] if slug.startswith('nt-') else slug
    url = f"https://edge.narto-drama.com/e/rs/detail/watch/{narto_slug}/1/refresh-source?force=1&lang=es-ES"
    try:
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0', 'Referer': 'https://narto-drama.com/'}, timeout=6)
        if r.status_code == 200 and r.json().get('ok'):
            data = r.json()
            play_url = data.get('play_url') or data.get('direct_play_url')
            # Check if playable
            hdrs = {'User-Agent': 'Mozilla/5.0', 'Referer': 'https://narto-drama.com/'}
            v_res = requests.get(play_url, headers=hdrs, stream=True, timeout=6)
            if v_res.status_code in (200, 206):
                working.append((slug, play_url[:60]))
                print(f"[OK 200] {slug}")
            else:
                broken.append((slug, v_res.status_code, v_res.text[:50]))
                print(f"[FAIL {v_res.status_code}] {slug} -> {v_res.text[:40]}")
        else:
            broken.append((slug, r.status_code, 'edge not ok'))
            print(f"[EDGE FAIL {r.status_code}] {slug}")
    except Exception as e:
        broken.append((slug, 0, str(e)))
        print(f"[ERR] {slug}: {e}")

print(f"\nSummary: {len(working)} working, {len(broken)} broken")
