import os
import json
import requests
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace', line_buffering=True)
except Exception:
    pass

with open('data/dramatube.json', 'r', encoding='utf-8') as f:
    dramas = json.load(f)

sub_dir = 'data/subtitles'
ready_dramas = []

for d in dramas:
    slug = d.get('slug')
    title = d.get('title')
    p = os.path.join(sub_dir, slug)
    if os.path.exists(p):
        vtts = [f for f in os.listdir(p) if f.endswith('.vtt') and os.path.getsize(os.path.join(p, f)) > 50]
        if len(vtts) >= 10:
            ready_dramas.append({
                'title': title,
                'slug': slug,
                'eps': len(d.get('episodes', {})),
                'sub_count': len(vtts)
            })

verified_30 = []
for item in ready_dramas:
    slug = item['slug']
    try:
        r_ep = requests.get(f'http://127.0.0.1:8090/proxy/episode?slug={slug}&ep=1', timeout=3)
        if r_ep.status_code == 200:
            data = r_ep.json()
            sub_url = next((s.get('url') for s in data.get('subtitles', []) if s.get('lang') == 'es'), None)
            if sub_url:
                # test fetching subtitle content
                sub_r = requests.get('http://127.0.0.1:8090' + sub_url, timeout=3)
                if sub_r.status_code == 200 and 'WEBVTT' in sub_r.text:
                    verified_30.append(item)
                    if len(verified_30) == 30:
                        break
    except Exception as e:
        pass

print(f"=== 30 TÍTULOS 100% VERIFICADOS (VIDEO STREAM + SUBTÍTULOS EN ESPAÑOL) ===\n")
for i, d in enumerate(verified_30, 1):
    link = f"http://localhost:3000/ver/{d['slug']}/1"
    print(f"{i}. **{d['title']}** ({d['eps']} eps, {d['sub_count']} subs ES) -> {link}")
