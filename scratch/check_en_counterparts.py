import requests
import json
import xml.etree.ElementTree as ET
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'

# Let's check sitemap for EN dramas
r_sm = requests.get('https://www.kurzdrama.com/sitemap.xml', headers={'User-Agent': UA}, timeout=10)
root = ET.fromstring(r_sm.content)

en_urls = []
for loc in root.iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc'):
    u = loc.text.strip()
    if '/en/episodes/' in u:
        en_urls.append(u)

print(f"Total /en/ episode URLs: {len(en_urls)}")

# Check if any EN drama has an /es/ counterpart that wasn't in the sitemap
es_slugs_found = []
for u in en_urls[:30]:
    # Try replacing /en/ with /es/
    es_u = u.replace('/en/', '/es/')
    try:
        r = requests.head(es_u, headers={'User-Agent': UA}, timeout=4, allow_redirects=True)
        if r.status_code == 200:
            es_slugs_found.append(es_u)
    except:
        pass

print(f"EN dramas that respond 200 on /es/: {len(es_slugs_found)} out of 30 tested")
for eu in es_slugs_found[:5]:
    print("  ", eu)
