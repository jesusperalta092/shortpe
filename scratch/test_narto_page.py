import requests
import re

url = 'https://narto-drama.com/detail/watch/ecos-de-la-fatalidad/1?lang=es-ES'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://narto-drama.com/'
}

r = requests.get(url, headers=headers, timeout=10)
print('Status:', r.status_code)
print('Length:', len(r.text))

matches = re.findall(r'https?://[^\s"\'<>]+', r.text)
print(f'Total URLs found: {len(matches)}')
for s in matches:
    if any(k in s.lower() for k in ['video', 'm3u8', 'stream', 'sansekai', 'vividshort', 'mp4', 'api', 'play']):
        print('->', s[:140])
