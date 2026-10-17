import urllib.request
import urllib.parse

slugs_to_test = [
    'dt-peÃ³n-abandonado-rey-dragÃ³n-inigualable-6a8280dc24d5639f6c0666af',
    'dt-pe%C3%83%C2%B3n-abandonado-rey-drag%C3%83%C2%B3n-inigualable-6a8280dc24d5639f6c0666af',
    'dt-peon-abandonado-rey-dragon-inigualable-6a8280dc24d5639f6c0666af',
    '6a8280dc24d5639f6c0666af'
]

for s in slugs_to_test:
    url = f"http://127.0.0.1:8090/api/dramatube/item?slug={urllib.parse.quote(s)}"
    try:
        res = urllib.request.urlopen(url)
        print(f"Slug: {s[:40]}... -> STATUS {res.status}")
    except Exception as e:
        print(f"Slug: {s[:40]}... -> ERROR: {e}")
