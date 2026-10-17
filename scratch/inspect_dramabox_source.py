import requests, re, json

url = 'https://narto-drama.com/detail/watch/aventura-prohibida-con-el-papa-de-mi-mejor-amiga-doblado/1?lang=es-ES'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://narto-drama.com/'
}
r = requests.get(url, headers=headers, timeout=10)
idx = r.text.find('episodeItemsRaw')
if idx != -1:
    print(r.text[idx: idx + 800])
