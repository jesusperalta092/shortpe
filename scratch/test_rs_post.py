import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
headers = {
    'User-Agent': UA,
    'Referer': 'https://www.reelshort.com/es',
    'Content-Type': 'application/json'
}

r = requests.post('https://www.reelshort.com/api/ms/hall/webInfo', json={"locale": "es"}, headers=headers, timeout=10)
print("POST webInfo:", r.status_code, "len:", len(r.text))
if r.status_code == 200:
    res = r.json()
    print("Keys:", list(res.keys()))
    print("res code/data:", res.get('code'), list(res.get('data', {}).keys()) if isinstance(res.get('data'), dict) else res.get('data'))
