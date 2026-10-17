import json, requests, re, time, concurrent.futures

hd = json.load(open('data/hotdrama.json', encoding='utf-8'))
print(f"Probando resolución on-demand para los {len(hd)} dramas de HotDrama...")

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Referer': 'https://narto-drama.com/'
}

def test_resolve(d):
    slug = d['slug']
    title = d.get('title')
    narto_slug = slug[3:] if slug.startswith('nt-') else slug
    url = f'https://narto-drama.com/detail/watch/{narto_slug}/1?lang=es-ES'
    try:
        r = requests.get(url, headers=headers, timeout=8)
        if r.status_code != 200:
            return slug, title, False, f"Page {r.status_code}"
        m = re.search(r'(https?://[^\s"\'<>]+(?:vigloo-stream|dramabox-stream|stream)[^\s"\'<>]*)', r.text)
        if not m:
            return slug, title, False, "No stream regex"
        stream_url = m.group(1).rstrip('`";,')
        # Probar stream URL
        r2 = requests.get(stream_url, headers={'User-Agent': headers['User-Agent'], 'Range': 'bytes=0-10'}, timeout=6)
        if r2.status_code in (200, 206):
            return slug, title, True, "OK (200/206)"
        return slug, title, False, f"Stream {r2.status_code}"
    except Exception as e:
        return slug, title, False, str(e)[:30]

with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    results = list(executor.map(test_resolve, hd))

ok = [r for r in results if r[2]]
fail = [r for r in results if not r[2]]

print(f"\nResultado final: {len(ok)} OK, {len(fail)} Fallidos de {len(hd)}")
print("\n--- DETALLE DE FUNCIONANDO ---")
for s, t, _, msg in ok:
    print(f"  [OK] {s}: {t} ({msg})")

print("\n--- DETALLE DE FALLIDOS ---")
for s, t, _, msg in fail:
    print(f"  [FAIL] {s}: {t} ({msg})")
