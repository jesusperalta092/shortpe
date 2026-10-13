import requests, re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Referer': 'https://narto-drama.com/'
}
url = 'https://narto-drama.com/detail/watch/ji-ge-yao-wo/1?lang=es-ES'
r = requests.get(url, headers=headers, timeout=10)
print('Page length:', len(r.text))

# Search for any stream or video URLs
matches = re.findall(r'https?://[^\s"\'<>]+(?:vigloo|stream|mp4|m3u8)[^\s"\'<>]*', r.text)
print('Found matches:', len(matches))
for m in matches[:10]:
    print('Match:', m[:120])
    if 'vigloo' in m or '.mp4' in m or '.m3u8' in m:
        try:
            head_r = requests.head(m, headers={'User-Agent': headers['User-Agent'], 'Referer': 'https://narto-drama.com/'}, timeout=5)
            print('   -> Status:', head_r.status_code)
        except Exception as e:
            print('   -> Err:', e)
