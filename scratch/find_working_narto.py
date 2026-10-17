import requests, json

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest'
}

keywords = ['doblado', 'espanol', 'amor', 'ceo', 'venganza', 'reina']
found_slugs = {}

for kw in keywords:
    url = f'https://narto-drama.com/search?q={kw}&limit=50&lang=es-ES'
    try:
        r = requests.get(url, headers=headers, timeout=10)
        items = r.json().get('items', [])
        for it in items:
            u = it.get('url', '')
            if '/detail/watch/' in u:
                s = u.split('/detail/watch/')[1].split('?')[0]
                if s not in found_slugs:
                    found_slugs[s] = (it.get('title'), it.get('poster_url'))
    except Exception as e:
        print(f"Err {kw}: {e}")

print(f"Total unique search dramas: {len(found_slugs)}")

# Test which ones are actually playable on episode 1 via edge
playable = []
for s, (title, poster) in list(found_slugs.items())[:35]:
    edge_url = f"https://edge.narto-drama.com/e/rs/detail/watch/{s}/1/refresh-source?force=1&lang=es-ES"
    try:
        r = requests.get(edge_url, headers={'User-Agent': 'Mozilla/5.0', 'Referer': 'https://narto-drama.com/'}, timeout=6)
        if r.status_code == 200 and r.json().get('ok'):
            purl = r.json().get('play_url') or r.json().get('direct_play_url')
            if purl:
                v = requests.get(purl, headers={'User-Agent': 'Mozilla/5.0'}, stream=True, timeout=5)
                if v.status_code in (200, 206):
                    playable.append({
                        'slug': f"nt-{s}",
                        'title': title,
                        'poster': poster,
                        'stream_sample': purl[:60]
                    })
                    print(f"[PLAYABLE 200] {title} ({s})", flush=True)
                else:
                    print(f"[STREAM ERR {v.status_code}] {title} ({s})", flush=True)
            else:
                print(f"[NO URL] {title}", flush=True)
        else:
            print(f"[EDGE FAIL {r.status_code}] {title}", flush=True)
    except Exception as e:
        print(f"[ERR] {title}: {e}", flush=True)

print(f"\nFound {len(playable)} playable fresh dramas!")
open('scratch/fresh_playable_narto.json', 'w', encoding='utf-8').write(json.dumps(playable, indent=2, ensure_ascii=False))
