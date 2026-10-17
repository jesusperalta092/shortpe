import requests, re, sys

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
slug = 'nt-bussy-and-the-beast'
ep = 1
narto_slug = slug[3:] if slug.startswith('nt-') else slug
url = f'https://narto-drama.com/detail/watch/{narto_slug}/{ep}?lang=es-ES'
print('Fetching:', url)
try:
    r = requests.get(url, headers={'User-Agent': UA, 'Referer': 'https://narto-drama.com/'}, timeout=8)
    print('Status:', r.status_code)
    m = re.search(r'(https?://[^\s"\'<>]+(?:vigloo-stream|dramabox-stream|stream)[^\s"\'<>]*)', r.text)
    if m:
        u = m.group(1).rstrip('`";,')
        print('Matched stream URL:', u[:90])
        r2 = requests.get(u, headers={'User-Agent': UA, 'Referer': 'https://narto-drama.com/', 'Range': 'bytes=0-10'}, timeout=5)
        print('Stream test status:', r2.status_code)
    else:
        print('No match, page text length:', len(r.text))
        print('Text sample:', r.text[:300])
except Exception as e:
    print('Error:', e)
