import requests, re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Referer': 'https://narto-drama.com/'
}
url = 'https://narto-drama.com/detail/watch/bussy-and-the-beast/1?lang=es-ES'
try:
    r = requests.get(url, headers=headers, timeout=10)
    print('Page status:', r.status_code)
    links = re.findall(r'https?://[^\s"\'<>]+', r.text)
    streams = [l for l in set(links) if 'vigloo' in l or 'dramabox' in l or 'stream' in l]
    print(f'Found {len(streams)} potential stream links:')
    for s in streams:
        print(' -', s[:120])
        try:
            hr = requests.head(s, headers=headers, timeout=5)
            print('    -> Status:', hr.status_code)
        except Exception as e:
            print('    -> Err:', e)
except Exception as e:
    print('Error:', e)
