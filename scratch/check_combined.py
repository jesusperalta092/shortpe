import json
import xml.etree.ElementTree as ET
import requests
import sys
import urllib.parse
sys.stdout.reconfigure(encoding='utf-8')

with open('scratch/kurz_parsed_home.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

home_slugs = set(urllib.parse.unquote(d.get('href', '').split('/episodes/')[-1].strip('/')) for d in data['dramas'])

r = requests.get("https://www.kurzdrama.com/sitemap.xml", headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
root = ET.fromstring(r.content)
sitemap_slugs = set()
for elem in root.iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc'):
    u = elem.text
    if '/es/episodes/' in u:
        s = urllib.parse.unquote(u.split('/episodes/')[-1].strip('/'))
        sitemap_slugs.add(s)

all_combined = home_slugs.union(sitemap_slugs)
print(f"Total COMBINED unique Spanish drama slugs: {len(all_combined)}")

print("\nSample slugs in sitemap not in home:")
for s in list(sitemap_slugs - home_slugs)[:5]:
    print("  ", s)
