import urllib.request, re, json

req = urllib.request.Request('https://esdramia.com/dramas/un-beso-de-navidad-de-mi-rival/1', headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
})
html = urllib.request.urlopen(req).read().decode('utf-8', errors='ignore')

# Search for any stream URLs, m3u8, mp4, api paths in the HTML
print("Matches for .mp4:")
for m in re.findall(r'https?://[^\s"\'<>]+\.mp4[^\s"\'<>]*', html):
    print("  MP4:", m[:120])

print("Matches for .m3u8:")
for m in re.findall(r'https?://[^\s"\'<>]+\.m3u8[^\s"\'<>]*', html):
    print("  M3U8:", m[:120])

print("Matches for /api/:")
for m in set(re.findall(r'/api/[a-zA-Z0-9_\-\/]+', html)):
    print("  API:", m)

# Let's inspect RSC payloads
chunks = re.findall(r'self\.__next_f\.push\(\[1,"(.+?)"\]\)', html)
full_rsc = ''.join(chunks)
print("RSC length:", len(full_rsc))
for m in re.finditer(r'https?://[^\s"\'\\]+', full_rsc):
    u = m.group(0)
    if 'video' in u or 'stream' in u or 'cdn' in u or 'media' in u:
        print("  RSC Video URL:", u[:120])
