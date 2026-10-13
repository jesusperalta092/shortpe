import requests
import re
import json

url = 'https://suikora.com/es/drama/mi-presa-facil-resulto-ser-el-rey-del-colegio/1'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8'
}

r = requests.get(url, headers=headers)
html = r.text

with open('scratch_suikora.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Status:", r.status_code)
print("Length:", len(html))

# Check for media URLs
media_urls = re.findall(r'https?://[^\s"\'<>]+\.(?:m3u8|mp4)[^\s"\'<>]*', html)
print(f"Found {len(media_urls)} media URLs:")
for u in media_urls[:10]:
    print(" -", u)

# Check for next_f payloads
next_f_chunks = re.findall(r'self\.__next_f\.push\(\[1,"(.*?)"\]\)', html)
print(f"Found {len(next_f_chunks)} self.__next_f chunks")

# Search for video / stream / episode keywords in html
for line in html.splitlines():
    if any(k in line.lower() for k in ['video', 'stream', 'episode', 'hls', 'player', 'm3u8', 'mp4']):
        # print first 200 chars of line
        print("Line snippet:", line[:160])
