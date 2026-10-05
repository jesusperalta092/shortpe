import requests, re, json

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Referer': 'https://netshort.com/',
    'Accept': 'application/json, text/plain, */*',
}

slug_id = 'claimed-by-three-alphas-2105968477965524993'

# Test common NetShort / Byterec API endpoints
endpoints = [
    f'https://netshort.com/api/drama/detail?id=2105968477965524993',
    f'https://netshort.com/api/episode/list?dramaId=2105968477965524993',
    f'https://netshort.com/api/episode/play?episodeId=2106272063794593796',
    f'https://api.netshort.com/v1/drama/detail?id=2105968477965524993',
    f'https://api.netshort.com/v1/episode/play?episodeId=2106272063794593796',
]

for ep in endpoints:
    try:
        r = requests.get(ep, headers=headers, timeout=10)
        print(f"GET {ep} -> Status: {r.status_code}, Length: {len(r.text)}, Content: {r.text[:150]}")
    except Exception as e:
        print(f"GET {ep} -> Error: {e}")
