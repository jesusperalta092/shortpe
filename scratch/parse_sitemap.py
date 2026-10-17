import requests
import re
import xml.etree.ElementTree as ET
import sys
sys.stdout.reconfigure(encoding='utf-8')

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
r = requests.get("https://www.kurzdrama.com/sitemap.xml", headers={'User-Agent': UA}, timeout=10)

root = ET.fromstring(r.content)
urls = [elem.text for elem in root.iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]

print(f"Total URLs in sitemap: {len(urls)}")
es_urls = [u for u in urls if '/es/' in u]
print(f"Total /es/ URLs: {len(es_urls)}")

es_episodes = [u for u in es_urls if '/episodes/' in u]
print(f"Total /es/ episode URLs: {len(es_episodes)}")

# Sample of es_urls
for u in es_urls[:10]:
    print("  ", u)
