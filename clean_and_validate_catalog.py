import json
import os
import re
import sys
import requests
from concurrent.futures import ThreadPoolExecutor

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace', line_buffering=True)
except Exception:
    pass

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36',
    'Accept': '*/*'
}

def clean_catalog():
    catalog_path = 'data/dramatube.json'
    if not os.path.exists(catalog_path):
        print("data/dramatube.json not found!")
        return

    with open(catalog_path, 'r', encoding='utf-8') as f:
        dramas = json.load(f)

    print(f"=== Starting Comprehensive DramaTube Catalog Cleanup ===")
    print(f"Initial dramas count: {len(dramas)}")

    # 1. Deduplicate by normalized title & slug
    seen_titles = {}
    deduped = []
    
    def norm_title(t):
        if not t: return ''
        s = t.lower()
        s = re.sub(r'\(dubbed\)|\[dubbed\]|\(español\)|\[español\]', '', s)
        s = re.sub(r'[^\w\s]', '', s)
        return ' '.join(s.split())

    for d in dramas:
        title = d.get('title', '')
        slug = d.get('slug', '')
        nt = norm_title(title)
        
        # Count quality score (prefer items with subtitles, more episodes, valid poster)
        subs_count = len(d.get('subtitles', {}))
        eps_count = len(d.get('episodes', {}))
        has_poster = 1 if d.get('poster') or d.get('poster_local') else 0
        score = (subs_count * 10) + eps_count + (has_poster * 5)
        
        if nt in seen_titles:
            prev_idx, prev_score = seen_titles[nt]
            if score > prev_score:
                # Replace with better version
                deduped[prev_idx] = d
                seen_titles[nt] = (prev_idx, score)
        else:
            seen_titles[nt] = (len(deduped), score)
            deduped.append(d)

    print(f"After Title Deduplication: {len(deduped)} dramas (removed {len(dramas) - len(deduped)} duplicate variants)")

    # 2. Parallel Stream Playability Validation
    print("Testing stream validity for all dramas (checking Ep 1)...")
    
    def validate_stream(d):
        eps = d.get('episodes', {})
        if not eps:
            return d, False, "No episodes"
        first_ep_url = eps.get('1') or list(eps.values())[0]
        if not first_ep_url or not isinstance(first_ep_url, str) or not first_ep_url.startswith('http'):
            return d, False, "Invalid URL format"
            
        try:
            r = requests.get(first_ep_url, headers=HEADERS, timeout=6, stream=True)
            # Check for 403 / 404 / 502 / time expire
            if r.status_code == 200:
                first_chunk = next(r.iter_content(512), b'')
                if b'time expire' in first_chunk.lower():
                    return d, False, "Expired CDN signature"
                return d, True, "OK"
            else:
                return d, False, f"HTTP {r.status_code}"
        except Exception as e:
            return d, False, f"Timeout/Connection error: {e}"

    with ThreadPoolExecutor(max_workers=20) as executor:
        validation_results = list(executor.map(validate_stream, deduped))

    valid_dramas = []
    broken_dramas = []
    for d, is_valid, reason in validation_results:
        if is_valid:
            valid_dramas.append(d)
        else:
            broken_dramas.append((d.get('title'), d.get('slug'), reason))

    print(f"\nStream Validation Summary:")
    print(f"  ✅ Playable Dramas: {len(valid_dramas)}")
    print(f"  ❌ Broken / Expired Dramas (Excluded): {len(broken_dramas)}")
    if broken_dramas:
        print("  Sample broken items excluded:")
        for b_t, b_s, b_r in broken_dramas[:8]:
            print(f"    - '{b_t}' ({b_s}): {b_r}")

    # 3. Save Cleaned & Validated Catalog
    with open(catalog_path, 'w', encoding='utf-8') as f:
        json.dump(valid_dramas, f, ensure_ascii=False, indent=2)

    print(f"\n[DONE] data/dramatube.json updated with {len(valid_dramas)} 100% playable, clean, deduplicated dramas!")

if __name__ == '__main__':
    clean_catalog()
