import re
import json

with open('scratch_suikora.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Let's find how the media URLs are stored in the HTML / JS
# Look for m3u8 URLs
urls = re.findall(r'https?://[^\s"\'<>]+\.m3u8[^\s"\'<>]*', text)
clean_urls = [u.rstrip('\\').rstrip('"').rstrip("'") for u in urls]
print(f"Total m3u8 URLs found: {len(clean_urls)}")
for i, u in enumerate(clean_urls, 1):
    print(f"Ep {i}: {u}")
