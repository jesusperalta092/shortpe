import requests, json

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Referer': 'https://netshort.com/episode/claimed-by-three-alphas-2105968477965524993',
    'Content-Type': 'application/json',
}

# Test short_play/episode_info
url = 'https://netshort.com/prod-web-api/web/v4/short_play/episode_info'
payloads = [
    {'dramaId': '2105968477965524993', 'episodeNo': 1},
    {'shortPlayId': '2105968477965524993', 'episodeNo': 1},
    {'episodeId': '2106272063794593796'},
]

for p in payloads:
    r = requests.post(url, headers=headers, json=p, timeout=10)
    print(f"POST {url} with {p} -> Status: {r.status_code}, Resp: {r.text[:200]}")
