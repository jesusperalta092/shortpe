import requests

url = 'https://videotv.vividshort.com/ocAES6GlMJMLlL5bhgYWsJBsQFFmIT1eCE4AFB?auth_key=1785345785-OuYfKXBr1n-0-9b49ed9529e096848eff5c9feb66799a'

referers = [
    '',
    'https://narto-drama.com/',
    'https://narto-drama.com/detail/watch/ecos-de-la-fatalidad/1?lang=es-ES',
    'https://vividshort.com/',
    'https://www.vividshort.com/',
    'https://esdramia.com/',
]

for ref in referers:
    hdrs = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36',
    }
    if ref:
        hdrs['Referer'] = ref
    try:
        r = requests.get(url, headers=hdrs, stream=True, timeout=5)
        chunk = next(r.iter_content(64), b'')
        print(f"Ref '{ref}': Status {r.status_code}, len={len(chunk)}, ct={r.headers.get('Content-Type')}")
    except Exception as e:
        print(f"Ref '{ref}': err {e}")
