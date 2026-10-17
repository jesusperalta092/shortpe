import requests
import re

url = 'https://narto-drama.com/detail/watch/ecos-de-la-fatalidad/1?lang=es-ES'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://narto-drama.com/'
}
r = requests.get(url, headers=headers, timeout=10)
html = r.text

scripts = re.findall(r'<script(?![^>]*src=)[^>]*>(.*?)</script>', html, re.DOTALL | re.I)
s13 = scripts[13]

idx = s13.find('refreshEpisodeSourceForPrefetch')
if idx != -1:
    print("=== refreshEpisodeSourceForPrefetch ===")
    print(s13[idx: idx + 1800])

idx2 = s13.find('currentSource')
if idx2 != -1:
    print("=== currentSource ===")
    print(s13[max(0, idx2 - 400): idx2 + 1000])
