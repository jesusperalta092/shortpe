import requests
import json
import re

url = 'https://dramix.tv/es/watch/aventura-prohibida-con-el-papa-de-mi-mejor-amiga-doblado/1'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
    'Referer': 'https://dramix.tv/'
}

r = requests.get(url, headers=headers)
html = r.text

chunks = re.findall(r'self\.__next_f\.push\(\[1,\s*"(.*?)"\s*\]\)', html, re.DOTALL)
for i, c in enumerate(chunks):
    decoded = bytes(c, "utf-8").decode("unicode_escape", "ignore")
    with open(f'_chunk_{i}.txt', 'w', encoding='utf-8') as f:
        f.write(decoded)
    print(f"Chunk {i} size: {len(decoded)}")
    if 'player' in decoded or 'video' in decoded or 'src' in decoded or 'source' in decoded:
        print(f"Found interesting keywords in Chunk {i}")
