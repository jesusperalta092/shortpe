import json
import xml.etree.ElementTree as ET
import requests
import sys
import urllib.parse
sys.stdout.reconfigure(encoding='utf-8')

# Load parsed homepage
with open('scratch/kurz_parsed_home.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

home_dramas = data['dramas']
home_slugs = set(urllib.parse.unquote(d.get('href', '').split('/episodes/')[-1].strip('/')) for d in home_dramas)

# Load sitemap
r = requests.get("https://www.kurzdrama.com/sitemap.xml", headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
root = ET.fromstring(r.content)
sitemap_slugs = set()
for elem in root.iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc'):
    u = elem.text
    if '/es/episodes/' in u:
        s = urllib.parse.unquote(u.split('/episodes/')[-1].strip('/'))
        sitemap_slugs.add(s)

print(f"Home unique slugs: {len(home_slugs)}")
print(f"Sitemap unique slugs: {len(sitemap_slugs)}")
overlap = home_slugs.intersection(sitemap_slugs)
print(f"Overlap: {len(overlap)}")
diff_home = home_slugs - sitemap_slugs
diff_site = sitemap_slugs - home_slugs
print(f"In home but not in sitemap: {len(diff_home)}")
print(f"In sitemap but not in home: {len(diff_site)}")
