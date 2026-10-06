import requests
import re
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Referer': 'https://narto-drama.com/'
}

r = requests.get('https://narto-drama.com/detail/watch/aventura-prohibida-con-el-papa-de-mi-mejor-amiga-doblado/2?lang=es-ES', headers=headers)
html = r.text

print("Narto HTML length:", len(html))

# Buscar video tags o scripts con data
videos = re.findall(r'https?://[^\s"\'<>]+\.(?:mp4|m3u8)[^\s"\'<>]*', html)
print("Direct videos in HTML:", len(videos), videos[:5])

# Buscar scripts con datos de episodios
scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
for i, s in enumerate(scripts):
    if 'episode' in s.lower() or 'source' in s.lower() or 'video' in s.lower() or '42000027513' in s:
        print(f"\nScript {i} ({len(s)} chars): {s[:300]}...")
        with open(f'_narto_script_{i}.txt', 'w', encoding='utf-8') as f:
            f.write(s)
