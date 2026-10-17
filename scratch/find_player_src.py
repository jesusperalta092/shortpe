import requests
import re

url = 'https://narto-drama.com/detail/watch/ecos-de-la-fatalidad/1?lang=es-ES'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://narto-drama.com/'
}
r = requests.get(url, headers=headers, timeout=10)
html = r.text

print("Video tags:")
for m in re.finditer(r'<video[^>]*>', html, re.I):
    print(m.group(0))

print("\nSource tags:")
for m in re.finditer(r'<source[^>]*>', html, re.I):
    print(m.group(0))

print("\nScript variables with src/video/stream:")
for m in re.finditer(r'(?:videoSrc|streamUrl|src|video_url|videoUrl|contentUrl)\s*[:=]\s*["\']([^"\']+)["\']', html, re.I):
    print(m.group(0))
