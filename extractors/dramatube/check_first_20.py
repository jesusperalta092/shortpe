import json, os, sys, requests

if sys.platform == 'win32':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except: pass

d = json.load(open('data/dramatube.json', encoding='utf-8'))
print(f"Total catalog count in data/dramatube.json: {len(d)}")

all_ok = True
for i, x in enumerate(d[:20], 1):
    title = x.get('title')
    poster = x.get('poster')
    try:
        r = requests.get(poster, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5, stream=True)
        if r.status_code == 200:
            ct = r.headers.get('Content-Type')
            print(f"[{i}] OK: {title} | {ct} | {poster[:50]}...")
        else:
            print(f"[{i}] FAIL ({r.status_code}): {title} | {poster}")
            all_ok = False
    except Exception as e:
        print(f"[{i}] ERR: {title} | {e}")
        all_ok = False

print("\nResult for first 20:", "100% OK" if all_ok else "Had failures")
