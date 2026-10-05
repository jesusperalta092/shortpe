import requests, re, json

url = 'https://netshort.com/episode/claimed-by-three-alphas-2105968477965524993'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
}

r = requests.get(url, headers=headers, timeout=20)
print(f"Status: {r.status_code}, Final URL: {r.url}, Length: {len(r.text)}")

# Extract Next.js RSC chunks
chunks = re.findall(r'self\.__next_f\.push\(\[1,"(.+?)"\]\)', r.text)
rsc = ''.join(chunks).encode().decode('unicode_escape', errors='ignore')
print(f"RSC length: {len(rsc)}")

# Let's search for drama info: title, description, cover, episodes, playVoucher
title_m = re.search(r'og:title" content="([^"]+)"', r.text)
img_m = re.search(r'og:image" content="([^"]+)"', r.text)
desc_m = re.search(r'og:description" content="([^"]+)"', r.text)

print("Title:", title_m.group(1) if title_m else None)
print("Image:", img_m.group(1) if img_m else None)
print("Desc:", desc_m.group(1)[:200] if desc_m else None)

# Check playVoucher
vouchers = re.findall(r'"playVoucher":"([^"]+)"', rsc)
print(f"Found {len(vouchers)} playVouchers")
if vouchers:
    print("Sample playVoucher:", vouchers[0][:150])

# Check episodes list in rsc
eps = re.findall(r'"episodeId":"(\d+)","episodeNo":(\d+)', rsc)
print(f"Found {len(eps)} episode matches. Sample:", eps[:5])

# Check all keys / objects in RSC
for k in ['videoUrl', 'videoPath', 'mp4', 'm3u8', 'cover', 'dramaName', 'total', 'chapter']:
    matches = re.findall(r'"' + k + r'":"?([^",}]+)"?', rsc)
    if matches:
        print(f"Key '{k}':", matches[:3])
