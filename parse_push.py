import urllib.request, re, json

req = urllib.request.Request('https://esdramia.com/dramas/un-beso-de-navidad-de-mi-rival/1', headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
})
html = urllib.request.urlopen(req).read().decode('utf-8', errors='ignore')

# Extract all push arguments
chunks = re.findall(r'self\.__next_f\.push\(\[(\d+),"(.*?)"\]\)', html)
print("Chunks count:", len(chunks))

combined = ""
for code, payload in chunks:
    # payload is escaped string
    combined += payload

# Search for any stream or video data
print("Combined length:", len(combined))

# Let's search for "sources", "stream", "player", "hash", "episode"
for match in re.finditer(r'\\"(sources|stream|hash|video|episodes|media|hls|m3u8|mp4)\\"', combined):
    start = max(0, match.start() - 50)
    end = min(len(combined), match.end() + 250)
    print(f"Match [{match.group(1)}]: {combined[start:end]}")
    print("=" * 60)
