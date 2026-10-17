import json, requests, re

with open('data/hotdrama.json', encoding='utf-8') as f:
    items = json.load(f)

with open('scratch/fresh_playable_narto.json', encoding='utf-8') as f:
    candidates = json.load(f)

# Candidate pool (not already in items)
existing_slugs = {d['slug'] for d in items}
available_cands = [c for c in candidates if c['slug'] not in existing_slugs]

verified_items = []
print(f"Auditing {len(items)} items in hotdrama.json:")

for i, d in enumerate(items):
    slug = d['slug']
    ep_url = f"http://127.0.0.1:8090/proxy/episode?slug={slug}&ep=1&fresh=1"
    is_ok = False
    try:
        r = requests.get(ep_url, timeout=8)
        if r.status_code == 200:
            p_url = 'http://127.0.0.1:8090' + r.json()['player_url']
            r_str = requests.get(p_url, stream=True, timeout=8)
            if r_str.status_code in (200, 206):
                chunk = next(r_str.iter_content(512), b'')
                if len(chunk) > 0:
                    is_ok = True
    except Exception:
        pass

    if is_ok:
        print(f"[{i+1}/31] [OK 200] {d['title']}")
        verified_items.append(d)
    else:
        print(f"[{i+1}/31] [REPLACING BROKEN] {d['title']} ({slug})")
        # Find replacement
        replaced = False
        while available_cands and not replaced:
            cand = available_cands.pop(0)
            c_slug = cand['slug']
            # Test candidate
            c_ep_url = f"http://127.0.0.1:8090/proxy/episode?slug={c_slug}&ep=1&fresh=1"
            try:
                c_r = requests.get(c_ep_url, timeout=8)
                if c_r.status_code == 200:
                    c_purl = 'http://127.0.0.1:8090' + c_r.json()['player_url']
                    c_str = requests.get(c_purl, stream=True, timeout=8)
                    if c_str.status_code in (200, 206):
                        c_chk = next(c_str.iter_content(512), b'')
                        if len(c_chk) > 0:
                            clean_t = re.sub(r'^\s*[\(\[]\s*doblado\s*[\)\]]\s*', '', cand['title'], flags=re.I).strip()
                            new_entry = {
                                "slug": c_slug,
                                "title": clean_t or cand['title'],
                                "description": f"Ver serie completa {clean_t or cand['title']} doblada en español latino en alta definición HD gratis.",
                                "poster": cand['poster'],
                                "section": "hotdrama",
                                "source": "narto",
                                "total_episodes": 60,
                                "genres": ["HotDrama", "Doblado", "Romance", "Drama"]
                            }
                            verified_items.append(new_entry)
                            print(f"       -> Replaced with: {new_entry['title']} ({c_slug})")
                            replaced = True
            except Exception:
                pass

print(f"\nFinal Verified items count: {len(verified_items)}")
with open('data/hotdrama.json', 'w', encoding='utf-8') as f:
    json.dump(verified_items, f, indent=2, ensure_ascii=False)

print("data/hotdrama.json successfully verified and saved!")
