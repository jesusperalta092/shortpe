import requests
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

endpoints = [
    'https://www.reelshort.com/api/ms/hall/webInfo?locale=es',
    'https://www.reelshort.com/api/ms/hall/webInfo?locale=es-ES',
    'https://www.reelshort.com/api/ms/hall/webInfo?locale=es-419',
    'https://www.reelshort.com/api/ms/book/getCategoryList?locale=es',
    'https://www.reelshort.com/api/ms/hall/getRankList?locale=es',
    'https://www.reelshort.com/api/ms/hall/getMoreBooks?locale=es',
    'https://www.reelshort.com/api/ms/search/hotSearch?locale=es',
    'https://www.reelshort.com/api/ms/book/getSubjectList?locale=es',
    'https://www.reelshort.com/api/ms/tag/getTagList?locale=es',
]

for ep in endpoints:
    try:
        r = requests.get(ep, headers={'User-Agent': UA, 'Referer': 'https://www.reelshort.com/es'}, timeout=6)
        print(f"{ep} -> {r.status_code}, len={len(r.text)}")
        if r.status_code == 200:
            print("  sample:", r.text[:150])
    except Exception as e:
        print(f"{ep} -> err: {e}")
