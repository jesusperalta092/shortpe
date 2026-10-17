import requests
import sys
sys.stdout.reconfigure(encoding='utf-8')

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

for path in ['/robots.txt', '/sitemap.xml', '/es/sitemap.xml', '/sitemap_index.xml', '/es/all', '/es/browse', '/es/categories']:
    url = f"https://www.kurzdrama.com{path}"
    try:
        r = requests.get(url, headers={'User-Agent': UA}, timeout=6)
        print(f"{path} -> HTTP {r.status_code}, len: {len(r.text)}")
        if r.status_code == 200 and ('xml' in r.headers.get('content-type', '') or 'text' in r.headers.get('content-type', '')):
            print("   Preview:", r.text[:200].replace('\n', ' '))
    except Exception as e:
        print(f"{path} -> Error: {e}")
