import requests

h1 = '4ee848d8527a50fbd5beb0d572c7271b'

s = requests.Session()
# First visit drama page
r1 = s.get('https://esdramia.com/dramas/un-beso-de-navidad-de-mi-rival/1', headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
})
print("Page status:", r1.status_code, "cookies:", s.cookies.get_dict())

# Now call stream API with session
r2 = s.get(f'https://esdramia.com/api/stream/{h1}', headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': '*/*',
    'Referer': 'https://esdramia.com/dramas/un-beso-de-navidad-de-mi-rival/1',
    'x-requested-with': 'XMLHttpRequest',
})
print("API status:", r2.status_code, "body:", r2.text)
