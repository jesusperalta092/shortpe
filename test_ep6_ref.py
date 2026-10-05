import requests

h6 = '4c06be4a8c7b0ef05a2ec25d559d1e4c'

s = requests.Session()
r = s.get(f'https://esdramia.com/api/stream/{h6}', headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': '*/*',
    'Referer': 'https://esdramia.com/dramas/un-beso-de-navidad-de-mi-rival/6',
})
print("API status ep6:", r.status_code, "body:", r.text)
