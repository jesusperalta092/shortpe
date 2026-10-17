import requests, json

items = json.load(open('data/hotdrama.json', encoding='utf-8'))[:10]

print("Testing top 10 hero dramas playback:")
for i, d in enumerate(items):
    slug = d['slug']
    ep_url = f"http://127.0.0.1:8090/proxy/episode?slug={slug}&ep=1"
    try:
        r = requests.get(ep_url, timeout=10)
        if r.status_code != 200:
            print(f"[{i+1}] FAIL {r.status_code} on ep endpoint: {slug}")
            continue
        data = r.json()
        p_url = 'http://127.0.0.1:8090' + data['player_url']
        r_stream = requests.get(p_url, stream=True, timeout=10)
        chunk = next(r_stream.iter_content(512), b'')
        if r_stream.status_code in (200, 206) and len(chunk) > 0:
            print(f"[{i+1}] OK (Status {r_stream.status_code}, {len(chunk)} bytes) -> {d['title']}")
        else:
            print(f"[{i+1}] FAIL stream (Status {r_stream.status_code}) -> {d['title']}")
    except Exception as e:
        print(f"[{i+1}] ERR: {slug} -> {e}")
