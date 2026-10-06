import requests
import json
import re

url = 'https://dramix.tv/es/drama/aventura-prohibida-con-el-papa-de-mi-mejor-amiga-doblado'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
    'Referer': 'https://dramix.tv/'
}

r = requests.get(url, headers=headers)
html = r.text

# Extract all links (href)
links = set(re.findall(r'href=[\'"]([^\'"]+)[\'"]', html))
print("Found links:")
for l in sorted(links):
    if 'drama' in l or 'watch' in l or 'ep' in l:
        print("  -", l)

# Extract schema.org TVSeries
schema_match = re.findall(r'<script type="application/ld\+json">([^<]+)</script>', html)
for sc in schema_match:
    try:
        data = json.loads(sc)
        if data.get('@type') == 'TVSeries' or 'name' in data:
            print("\nSchema.org Data:")
            print("Name:", data.get('name'))
            print("Description:", data.get('description'))
            print("Image:", data.get('image'))
            print("Episodes count (numberOfEpisodes):", data.get('numberOfEpisodes'))
            print("Episode list in schema:", len(data.get('episode', [])))
            if data.get('episode'):
                print("First episode:", data['episode'][0])
    except Exception as e:
        pass
