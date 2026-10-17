import requests
import re
import xml.etree.ElementTree as ET
import sys
sys.stdout.reconfigure(encoding='utf-8')

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'

# 1. Check ReelShort sitemaps
print("=== 1. Checking Reelshort sitemap ===")
try:
    r = requests.get('https://www.reelshort.com/sitemap.xml', headers={'User-Agent': UA}, timeout=10)
    print("Reelshort sitemap.xml status:", r.status_code, "len:", len(r.text))
    if r.status_code == 200:
        root = ET.fromstring(r.content)
        sitemaps = [e.text for e in root.iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
        print(f"Sub-sitemaps in reelshort.com: {len(sitemaps)}")
        for sm in sitemaps[:10]:
            print("  ", sm)
except Exception as e:
    print("Reelshort sitemap error:", e)

# 2. Check Kurzdrama API or routes
print("\n=== 2. Checking Kurzdrama other sitemaps & routes ===")
for p in ['/sitemap_index.xml', '/sitemap-es.xml', '/es/sitemap-episodes.xml', '/api/search?q=a&locale=es', '/api/book/list?locale=es']:
    try:
        r = requests.get(f'https://www.kurzdrama.com{p}', headers={'User-Agent': UA}, timeout=6)
        print(f"kurzdrama {p} -> {r.status_code}, len: {len(r.text)}")
    except Exception as e:
        print(f"kurzdrama {p} -> error {e}")
