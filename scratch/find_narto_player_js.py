import requests
import re

url = 'https://narto-drama.com/detail/watch/ecos-de-la-fatalidad/1?lang=es-ES'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://narto-drama.com/'
}
r = requests.get(url, headers=headers, timeout=10)
html = r.text

# Extract all inline scripts
scripts = re.findall(r'<script(?![^>]*src=)[^>]*>(.*?)</script>', html, re.DOTALL | re.I)
print(f"Found {len(scripts)} inline scripts")

for i, s in enumerate(scripts):
    if any(k in s for k in ['player', 'video', 'episode', 'hls', 'fetch', 'api', 'source']):
        print(f"\n--- SCRIPT {i} (len={len(s)}) ---")
        lines = [line.strip() for line in s.split('\n') if any(w in line for w in ['player.src', 'fetch(', '$.ajax', 'loadSource', 'video_url', 'streamUrl', 'play(', 'initPlayer', 'setupPlayer'])]
        for l in lines[:30]:
            print("  ", l[:150])
