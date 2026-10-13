import json, requests, concurrent.futures

ds = json.load(open('data/dramashorts.json', encoding='utf-8'))
print(f'Auditing {len(ds)} items in dramashorts.json...')

def test_drama(d):
    slug = d['slug']
    title = d.get('title')
    ep1 = d.get('episodes', {}).get('1', '')
    if not ep1:
        return slug, title, 0, 'no_ep1'
    try:
        # Some CDNs need GET with range bytes=0-10
        r = requests.get(ep1, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)', 'Range': 'bytes=0-10'}, timeout=7)
        if r.status_code in (200, 206):
            return slug, title, r.status_code, 'ok'
        return slug, title, r.status_code, 'fail'
    except Exception as e:
        return slug, title, 0, str(e)[:30]

with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
    results = list(executor.map(test_drama, ds))

working = [r for r in results if r[3] == 'ok']
failed = [r for r in results if r[3] != 'ok']

print(f'\nTotal: {len(ds)} | Working: {len(working)} | Failed: {len(failed)}')
print('\nSample failed:')
for s, t, code, reason in failed[:10]:
    print(f'  [{code}] {s}: {t} ({reason})')
