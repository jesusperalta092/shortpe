import requests
import re
import urllib.parse

url = 'https://suikora.com/es/drama/doblado-amigas-contra-el-guion/1'
headers = {'User-Agent': 'Mozilla/5.0'}
html = requests.get(url, headers=headers).text

# Find links to genre or tags
genres = set()
for m in re.finditer(r'href="[^"]*genre=([^"&]+)"[^>]*>(.*?)</a>', html):
    g = urllib.parse.unquote(m.group(1)).capitalize()
    genres.add(g)

if not genres:
    for m in re.finditer(r'/es/dramas/tag/([^"/?#]+)', html):
        genres.add(urllib.parse.unquote(m.group(1)).capitalize())

print("Found genres:", list(genres))
