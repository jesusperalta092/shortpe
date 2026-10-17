import requests, re, json

url = 'https://narto-drama.com/detail/watch/aventura-prohibida-con-el-papa-de-mi-mejor-amiga-doblado/1?lang=es-ES'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Referer': 'https://narto-drama.com/'
}
try:
    r = requests.get(url, headers=headers, timeout=10)
    print('Status:', r.status_code)
    # Search for any streaming links or API endpoints
    links = re.findall(r'https?://[^\s"\'<>]+', r.text)
    streams = [l for l in set(links) if any(k in l.lower() for k in ['stream', 'video', 'vigloo', 'mp4', 'm3u8', 'play'])]
    print('Found streams in page:', len(streams))
    for s in streams[:10]:
        print(' -', s[:120])
except Exception as e:
    print('Error:', e)
