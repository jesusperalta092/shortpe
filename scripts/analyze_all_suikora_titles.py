import re
import xml.etree.ElementTree as ET
import requests

with open('suikora_sitemap.xml', 'r', encoding='utf-8') as f:
    text = f.read()

# Let's download or read dramas-es-0.xml
url = 'https://suikora.com/sitemap/dramas-es-0.xml'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'}
r = requests.get(url, headers=headers)
with open('dramas-es-0.xml', 'w', encoding='utf-8') as f:
    f.write(r.text)

urls = re.findall(r'<loc>(.*?)</loc>', r.text)
print(f"Total drama URLs in dramas-es-0.xml: {len(urls)}")

# Extract slugs
slugs = []
for u in urls:
    m = re.search(r'/es/drama/([^/]+)', u)
    if m:
        slugs.append(m.group(1))

print(f"Total slugs: {len(slugs)}")
print("Sample first 20 slugs:")
for s in slugs[:20]:
    # Convert slug to nice title
    title_approx = s.replace('-', ' ').capitalize()
    print(f" - [{s}] -> {title_approx}")
