import json, requests

d = json.load(open('data/dramatube.json', encoding='utf-8'))
print(f"Testing {len(d)} DramaTube titles...")

for item in d:
    slug = item['slug']
    title = item['title']
    res = requests.get(f'http://127.0.0.1:8090/proxy/episode?slug={slug}&ep=1')
    if res.status_code != 200:
        print(f"[FAIL] {title} ({slug}): status {res.status_code}")
        continue
    data = res.json()
    p_url = data.get('player_url')
    if not p_url:
        print(f"[FAIL] {title} ({slug}): no player_url")
        continue
    
    man_res = requests.get('http://127.0.0.1:8090' + p_url)
    if man_res.status_code != 200:
        print(f"[FAIL] {title} ({slug}): Manifest status {man_res.status_code}")
        continue
        
    lines = [l for l in man_res.text.splitlines() if l.startswith('/proxy/seg') or l.startswith('/proxy/manifest')]
    if not lines:
        print(f"[FAIL] {title} ({slug}): No segments in manifest")
        continue
        
    first_item = lines[0]
    if first_item.startswith('/proxy/manifest'):
        # Master playlist with variant
        v_res = requests.get('http://127.0.0.1:8090' + first_item)
        v_lines = [l for l in v_res.text.splitlines() if l.startswith('/proxy/seg')]
        if v_lines:
            seg_res = requests.get('http://127.0.0.1:8090' + v_lines[0])
            print(f"[OK Variant] {title}: Seg length={len(seg_res.content)} bytes | Type=HLS")
        else:
            print(f"[WARN] {title}: Variant playlist had no segs")
    else:
        seg_res = requests.get('http://127.0.0.1:8090' + first_item)
        print(f"[OK Direct] {title}: Seg length={len(seg_res.content)} bytes | Type=HLS")
