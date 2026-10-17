import requests
import re
from bs4 import BeautifulSoup
import sys
sys.stdout.reconfigure(encoding='utf-8')

reel_url = "https://www.reelshort.com/es/full-episodes/unida-al-alfa-y-su-beta-6a433648a0263ac457025610"
r = requests.get(reel_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)

soup = BeautifulSoup(r.text, 'html.parser')
links = soup.find_all('a', href=True)

episodes = []
for a in links:
    href = a['href']
    if '/episodes/' in href:
        slug = href.split('/episodes/')[-1].strip('/')
        # Extract number if any
        num_m = re.search(r'episode-(\d+)', slug, re.IGNORECASE)
        num = int(num_m.group(1)) if num_m else 0
        title = a.get_text(strip=True) or f"Episodio {num}"
        episodes.append({'href': href, 'slug': slug, 'number': num, 'title': title})

# Deduplicate
seen = set()
unique_eps = []
for ep in episodes:
    if ep['slug'] not in seen:
        seen.add(ep['slug'])
        unique_eps.append(ep)

print(f"Total unique episodes found on page 1: {len(unique_eps)}")
for ep in unique_eps[:5]:
    print("  ", ep)

# Check pagination
pag_links = re.findall(r'/full-episodes/[^"\'\s>]+/(\d+)', r.text)
print("Pagination numbers found:", set(pag_links))
