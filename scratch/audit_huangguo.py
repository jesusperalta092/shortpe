import json, requests, concurrent.futures

hg = json.load(open('data/huangguo.json', encoding='utf-8'))
print(f'Auditing {len(hg)} items in huangguo.json...')

def test_drama(d):
    slug = d['slug']
    title = d.get('title')
    ep1 = d.get('episodes', {}).get('1', '')
    if not ep1:
        return slug, title, 0, 'no_ep1'
    try:
        r = requests.get(ep1, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)', 'Range': 'bytes=0-10'}, timeout=7)
        if r.status_code in (200, 206):
            return slug, title, r.status_code, 'ok'
        return slug, title, r.status_code, 'fail'
    except Exception as e:
        return slug, title, 0, str(e)[:30]

with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
    results = list(executor.map(test_drama, hg))

working = [r for r in results if r[3] == 'ok']
failed = [r for r in results if r[3] != 'ok']

print(f'\nTotal: {len(hg)} | Working: {len(working)} | Failed: {len(failed)}')
if failed:
    print('Sample failed:')
    for s, t, code, reason in failed[:5]:
        print(f'  [{code}] {s}: {t} ({reason})')
