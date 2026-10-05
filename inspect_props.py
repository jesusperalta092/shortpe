import urllib.request, re

req = urllib.request.Request('https://esdramia.com/dramas/un-beso-de-navidad-de-mi-rival/1', headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36',
})
html = urllib.request.urlopen(req).read().decode('utf-8', errors='ignore')

chunks = re.findall(r'self\.__next_f\.push\(\[(\d+),"(.*?)"\]\)', html)
combined = "".join(c[1] for c in chunks)

idx = combined.find('initialIndex')
if idx != -1:
    print(combined[idx-100:idx+600])
