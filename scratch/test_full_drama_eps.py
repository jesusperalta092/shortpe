import requests
import re
from bs4 import BeautifulSoup
import sys
sys.stdout.reconfigure(encoding='utf-8')

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

# Let's get all pages of episodes for this drama
book_slug = "unida-al-alfa-y-su-beta-6a433648a0263ac457025610"
base_reel = f"https://www.reelshort.com/es/full-episodes/{book_slug}"

all_episodes = []
seen_slugs = set()

# First page
r = requests.get(base_reel, headers={'User-Agent': UA}, timeout=10)
# Find max page
pages = [1]
for p in re.findall(r'/full-episodes/[^"\'\s>]+/(\d+)', r.text):
    pages.append(int(p))
max_page = max(pages) if pages else 1
print(f"Total pages for {book_slug}: {max_page}")

def parse_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    for a in soup.find_all('a', href=True):
        href = a['href']
        if '/episodes/' in href:
            slug = href.split('/episodes/')[-1].strip('/')
            if slug not in seen_slugs:
                seen_slugs.add(slug)
                num_m = re.search(r'episode-(\d+)', slug, re.IGNORECASE)
                num = int(num_m.group(1)) if num_m else 0
                title = a.get_text(strip=True) or f"Episodio {num}"
                all_episodes.append({'number': num, 'slug': slug, 'title': title})

parse_html(r.text)

for p in range(2, max_page + 1):
    rp = requests.get(f"{base_reel}/{p}", headers={'User-Agent': UA}, timeout=10)
    parse_html(rp.text)

all_episodes.sort(key=lambda x: x['number'])
print(f"Total episodes scraped for drama: {len(all_episodes)}")
print(f"First episode: {all_episodes[0]}")
print(f"Last episode: {all_episodes[-1]}")

# Test checking m3u8 for ep 1, ep 15, ep 30, last ep
test_indices = [0, min(14, len(all_episodes)-1), min(29, len(all_episodes)-1), len(all_episodes)-1]
for idx in set(test_indices):
    ep = all_episodes[idx]
    ep_url = f"https://www.kurzdrama.com/es/episodes/{ep['slug']}"
    res = requests.get(ep_url, headers={'User-Agent': UA}, timeout=10)
    m3u8_m = re.findall(r'https?://v-mps\.crazymaplestudios\.com/[^\s"\'<>]+\.m3u8', res.text)
    print(f"Ep {ep['number']} ({ep['slug'][:30]}...): HTTP {res.status_code}, m3u8 count: {len(m3u8_m)}")
    if m3u8_m:
        print(f"   m3u8 sample: {m3u8_m[0][:70]}...")
