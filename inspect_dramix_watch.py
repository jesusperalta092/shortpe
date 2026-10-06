import requests
import json
import re

url = 'https://dramix.tv/es/watch/aventura-prohibida-con-el-papa-de-mi-mejor-amiga-doblado/1'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
    'Referer': 'https://dramix.tv/'
}

r = requests.get(url, headers=headers)
html = r.text
print(f"Watch Ep 1 status: {r.status_code}, len: {len(html)}")

# Buscar videos mp4, m3u8, CDN urls, scripts
video_urls = re.findall(r'https?://[^\s"\'<>]+\.(?:mp4|m3u8)[^\s"\'<>]*', html)
print("\nDirect video URLs found:", video_urls)

# Buscar todas las URLs sospechosas
all_cdn_urls = re.findall(r'https?://[^\s"\'<>]*(?:video|stream|media|play|cdn|chunk|hls|m3u8|dramabox|goodshort|shortmax|s3)[^\s"\'<>]*', html, re.IGNORECASE)
print("\nCDN / Media URLs found:")
for u in set(all_cdn_urls):
    print("  -", u[:120])

# Buscar scripts con datos de reproductor
scripts = re.findall(r'self\.__next_f\.push\(\[1,"(.*?)"\]\)', html, re.DOTALL)
print(f"\nFound {len(scripts)} RSC chunks")
for i, chunk in enumerate(scripts):
    if 'mp4' in chunk or 'm3u8' in chunk or 'video' in chunk or 'stream' in chunk or '172108' in chunk:
        print(f"\nChunk {i} snippet:")
        print(chunk[:500].encode('utf-8', 'ignore').decode('utf-8'))
