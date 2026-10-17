import urllib.request
import xml.etree.ElementTree as ET
import re
import json

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
req = urllib.request.Request('https://www.kurzdrama.com/sitemap.xml', headers={'User-Agent': UA})
content = urllib.request.urlopen(req).read()
root = ET.fromstring(content)

by_lang = {}
all_urls = []
for loc in root.iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc'):
    u = loc.text.strip()
    all_urls.append(u)
    m = re.search(r'kurzdrama\.com/([a-z\-]+)/', u)
    lang = m.group(1) if m else 'root'
    by_lang.setdefault(lang, []).append(u)

print("Total URLs in sitemap:", len(all_urls))
for lang, urls in by_lang.items():
    print(f"  {lang}: {len(urls)} URLs")

# Let's see sample URLs in ES
print("\nSample ES URLs in sitemap:")
for u in by_lang.get('es', [])[:10]:
    print(" ", u)
