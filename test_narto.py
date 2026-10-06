import requests
import json

url = 'https://narto-drama.com/api/drama/aventura-prohibida-con-el-papa-de-mi-mejor-amiga-doblado'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Referer': 'https://narto-drama.com/'
}

r = requests.get(url, headers=headers)
print("narto API status:", r.status_code)
print(r.text[:500])

r_page = requests.get('https://narto-drama.com/detail/watch/aventura-prohibida-con-el-papa-de-mi-mejor-amiga-doblado/2?lang=es-ES', headers=headers)
print("narto watch ep2 status:", r_page.status_code, len(r_page.text))
