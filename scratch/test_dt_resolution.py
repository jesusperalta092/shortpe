import json
import requests
import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
HEADERS = {'User-Agent': UA, 'Referer': 'https://www.kurzdrama.com/'}

with open('data/dramatube.json', 'r', encoding='utf-8') as f:
    dramas = json.load(f)

dt_map = {d['slug']: d for d in dramas}
sample = dt_map['dt-unida-al-alfa-y-su-beta-6a433648a0263ac457025610']

def resolve_ep(dt, ep):
    eps = dt.get('episodes', {})
    ep_data = eps.get(str(ep))
    if not ep_data:
        return None
    if ep_data.get('m3u8'):
        return ep_data['m3u8']
    
    ep_slug = ep_data.get('slug')
    if not ep_slug:
        return None
    
    url = f"https://www.kurzdrama.com/es/episodes/{ep_slug}"
    r = requests.get(url, headers=HEADERS, timeout=8)
    m = re.search(r'https?://v-mps\.crazymaplestudios\.com/[^\s"\'<>]+\.m3u8', r.text)
    if m:
        m3u8 = m.group(0)
        ep_data['m3u8'] = m3u8
        return m3u8
    return None

for test_ep in [1, 2, 10, 25, 50]:
    stream = resolve_ep(sample, test_ep)
    print(f"Episode {test_ep}: {stream[:70]}..." if stream else f"Episode {test_ep}: FAILED")
