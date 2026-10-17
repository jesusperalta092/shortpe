import requests, re, time

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Referer': 'https://narto-drama.com/'
}

def resolve_narto_stream(slug, ep=1):
    # Strip nt- prefix
    narto_slug = slug[3:] if slug.startswith('nt-') else slug
    url = f'https://narto-drama.com/detail/watch/{narto_slug}/{ep}?lang=es-ES'
    try:
        t0 = time.time()
        r = requests.get(url, headers=headers, timeout=8)
        if r.status_code != 200:
            return None, f"HTTP {r.status_code}"
        # Search for vigloo or dramabox or media stream URL
        m = re.search(r'(https?://[^\s"\'<>]+(?:vigloo-stream|dramabox-stream|stream)[^\s"\'<>]*)', r.text)
        if m:
            stream_url = m.group(1).rstrip('`";,')
            dt = time.time() - t0
            return stream_url, f"OK ({dt:.2f}s)"
        return None, "No stream url pattern matched"
    except Exception as e:
        return None, str(e)

for ep in [1, 2, 5]:
    stream, msg = resolve_narto_stream('nt-bussy-and-the-beast', ep)
    print(f"Ep {ep}: {msg}")
    if stream:
        print("  Stream:", stream[:90] + "...")
        # Test stream HEAD/GET
        r_test = requests.get(stream, headers={'User-Agent': headers['User-Agent'], 'Range': 'bytes=0-10'}, timeout=5)
        print("  Stream response:", r_test.status_code)
