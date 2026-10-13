import re
import json

with open('scratch_suikora.html', 'r', encoding='utf-8') as f:
    text = f.read()

print("HTML Length:", len(text))

# Find title in <title> or <h1>
title_m = re.search(r'<title>(.*?)</title>', text)
print("Title tag:", title_m.group(1) if title_m else "None")

h1_m = re.search(r'<h1[^>]*>(.*?)</h1>', text)
print("H1 tag:", h1_m.group(1) if h1_m else "None")

# Find description or synopsis
desc_m = re.search(r'<meta\s+name="description"\s+content="([^"]*)"', text)
print("Description:", desc_m.group(1) if desc_m else "None")

# Find poster or image
og_img = re.search(r'<meta\s+property="og:image"\s+content="([^"]*)"', text)
print("OG Image:", og_img.group(1) if og_img else "None")

# Find episode links
eps = re.findall(r'/es/drama/[^/]+/(\d+)', text)
ep_nums = sorted(list(set(int(x) for x in eps)))
print(f"Unique episode numbers in page: {len(ep_nums)} -> {ep_nums}")

# Check self.__next_f pushes
pushes = re.findall(r'self\.__next_f\.push\(\[1,\s*"(.*?)"\]\)', text)
print(f"self.__next_f pushes count: {len(pushes)}")
for i, p in enumerate(pushes):
    # unescape python-style string
    try:
        decoded = p.encode('utf-8').decode('unicode_escape')
        if 'akamai-static' in decoded or 'main.m3u8' in decoded or 'episode' in decoded.lower():
            print(f"\n--- Push #{i} (len {len(decoded)}) ---")
            print(decoded[:500])
    except Exception as e:
        pass
