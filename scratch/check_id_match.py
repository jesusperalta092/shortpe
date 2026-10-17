import json
import xml.etree.ElementTree as ET
import requests
import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('scratch/kurz_parsed_home.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

def extract_hex_id(url_or_slug):
    m = re.search(r'([a-f0-9]{24})', url_or_slug)
    return m.group(1) if m else None

home_ids = set()
for d in data['dramas']:
    hid = extract_hex_id(d.get('href', ''))
    if hid:
        home_ids.add(hid)

r = requests.get("https://www.kurzdrama.com/sitemap.xml", headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
root = ET.fromstring(r.content)
sitemap_ids = set()
for elem in root.iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc'):
    u = elem.text
    if '/es/episodes/' in u:
        sid = extract_hex_id(u)
        if sid:
            sitemap_ids.add(sid)

print(f"Unique book IDs in home: {len(home_ids)}")
print(f"Unique book IDs in sitemap: {len(sitemap_ids)}")
print(f"Overlap: {len(home_ids.intersection(sitemap_ids))}")
print(f"In sitemap not in home: {len(sitemap_ids - home_ids)}")
print(f"In home not in sitemap: {len(home_ids - sitemap_ids)}")
