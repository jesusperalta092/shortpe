import requests, re

url = 'https://narto-drama.com/detail/watch/aventura-prohibida-con-el-papa-de-mi-mejor-amiga-doblado/1?lang=es-ES'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://narto-drama.com/'
}
r = requests.get(url, headers=headers, timeout=10)
print('Status:', r.status_code)

matches = re.findall(r'https?://[^\s"\'<>]+', r.text)
for s in matches:
    if any(k in s.lower() for k in ['m3u8', 'mp4', 'stream', 'sansekai', 'dramabox', 'vividshort', 'flextv']):
        if not any(k in s.lower() for k in ['google', 'turnstile', 'jquery', 'jsdelivr', 'sweetalert']):
            print('->', s[:140])
