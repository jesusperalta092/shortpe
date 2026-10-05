import urllib.request, re, json

req = urllib.request.Request('https://esdramia.com/dramas/un-beso-de-navidad-de-mi-rival/1', headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
})
html = urllib.request.urlopen(req).read().decode('utf-8', errors='ignore')

# Dump all occurrences of "sources", "video", "url", "stream" in the html
for line in html.split('\n'):
    if any(k in line for k in ['sources', 'stream', 'episode', 'hash']):
        print(line[:300])
        print("---")
