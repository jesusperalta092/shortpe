import urllib.request, re, json

req = urllib.request.Request('https://esdramia.com/dramas/un-beso-de-navidad-de-mi-rival/1', headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
})
html = urllib.request.urlopen(req).read().decode('utf-8', errors='ignore')

print("Total HTML length:", len(html))
# Let's find all script tags
scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
print(f"Found {len(scripts)} scripts")
for i, s in enumerate(scripts):
    if len(s) > 50:
        print(f"Script {i}: {s[:300]}")
        print("...")
