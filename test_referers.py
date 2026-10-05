import requests

h6 = '4c06be4a8c7b0ef05a2ec25d559d1e4c'

test_referers = [
    'https://esdramia.com/',
    'https://esdramia.com/dramas/un-beso-de-navidad-de-mi-rival/6',
    'https://esdramia.com/dramas/un-beso-de-navidad-de-mi-rival/1',
]

for ref in test_referers:
    s = requests.Session()
    r = s.get(f'https://esdramia.com/api/stream/{h6}', headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Referer': ref,
    })
    print(f"Referer: {ref} -> Status: {r.status_code}")
