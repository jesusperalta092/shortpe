import urllib.request
import urllib.parse
import json
import re
import os
import time
import sys

# Ensure UTF-8 stdout encoding and unbuffered output on Windows
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace', line_buffering=True)
except Exception:
    pass

# Rate limiting and safe headers
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': '*/*'
}

def wrap_subtitle_text(text, max_len=52):
    """Formats subtitle lines naturally: keeps single sentences together (up to 52 chars) and splits only long sentences."""
    if not text:
        return ""
    single_line = ' '.join(text.strip().split())
    if len(single_line) <= max_len:
        return single_line
        
    words = single_line.split()
    lines = []
    curr = []
    curr_len = 0
    for w in words:
        add_len = len(w) + (1 if curr else 0)
        if curr_len + add_len <= max_len:
            curr.append(w)
            curr_len += add_len
        else:
            if curr:
                lines.append(' '.join(curr))
            curr = [w]
            curr_len = len(w)
    if curr:
        lines.append(' '.join(curr))
    return '\n'.join(lines)

def translate_srt_to_es(srt_content):
    """Parses SRT content, translates dialogues to Spanish in batch, and returns Spanish WebVTT."""
    blocks = [b.strip() for b in re.split(r'\n\s*\n', srt_content.strip()) if b.strip()]
    
    parsed = []
    dialogues = []
    
    for b in blocks:
        lines = b.split('\n')
        if len(lines) >= 3 and '-->' in lines[1]:
            idx = lines[0]
            t = re.sub(r'(\d{2}:\d{2}:\d{2}),(\d{3})', r'\1.\2', lines[1])
            txt = ' '.join([l.strip() for l in lines[2:] if l.strip()])
            parsed.append({'idx': idx, 'timestamp': t, 'has_text': True})
            dialogues.append(txt)
        elif len(lines) >= 2 and '-->' in lines[1]:
            idx = lines[0]
            t = re.sub(r'(\d{2}:\d{2}:\d{2}),(\d{3})', r'\1.\2', lines[1])
            parsed.append({'idx': idx, 'timestamp': t, 'has_text': False})
        else:
            parsed.append({'raw': b, 'has_text': False})
            
    if not dialogues:
        return "WEBVTT\n\n"
        
    delimiter = "\n[[[---]]]\n"
    combined_text = delimiter.join(dialogues)
    
    # Retry loop with backoff
    for attempt in range(3):
        try:
            url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=es&dt=t&q={urllib.parse.quote(combined_text)}"
            req = urllib.request.Request(url, headers=HEADERS)
            res = urllib.request.urlopen(req, timeout=15)
            data = json.loads(res.read().decode('utf-8'))
            translated_full = ''.join([part[0] for part in data[0] if part[0]])
            break
        except Exception as e:
            if attempt == 2:
                print(f"      [!] Translation API failed after 3 attempts: {e}")
                translated_full = combined_text
            time.sleep(1.0 * (attempt + 1))
    
    translated_dialogues = re.split(r'\s*\[\[\[---\]\]\]\s*', translated_full)
    
    out_lines = ["WEBVTT\n"]
    d_idx = 0
    for item in parsed:
        if item.get('has_text'):
            raw_t = translated_dialogues[d_idx] if d_idx < len(translated_dialogues) else dialogues[d_idx]
            d_idx += 1
            t_txt = wrap_subtitle_text(raw_t, max_len=52)
            out_lines.append(f"{item['idx']}\n{item['timestamp']}\n{t_txt}\n")
        elif 'idx' in item:
            out_lines.append(f"{item['idx']}\n{item['timestamp']}\n")
        else:
            out_lines.append(f"{item.get('raw', '')}\n")
            
    return '\n'.join(out_lines)

def process_all_subtitles():
    catalog_path = os.path.join('data', 'dramatube.json')
    if not os.path.exists(catalog_path):
        print("Catalog data/dramatube.json not found!")
        return

    with open(catalog_path, 'r', encoding='utf-8') as f:
        catalog = json.load(f)

    # Filter dramas that have subtitles
    dramas_with_subs = [d for d in catalog if d.get('subtitles')]
    print(f"============================================================")
    print(f"Found {len(dramas_with_subs)} dramas with subtitle tracks in DramaTube catalog.")
    print(f"============================================================\n")

    total_translated_eps = 0
    total_skipped_eps = 0

    for d_idx, drama in enumerate(dramas_with_subs, start=1):
        slug = drama.get('slug')
        title = drama.get('title')
        subs = drama.get('subtitles', {})
        
        out_dir = os.path.join('data', 'subtitles', slug)
        os.makedirs(out_dir, exist_ok=True)
        
        ep_keys = sorted(subs.keys(), key=lambda x: int(x) if x.isdigit() else 999999)
        print(f"[{d_idx}/{len(dramas_with_subs)}] Processing: '{title}' ({len(ep_keys)} eps) [slug: {slug}]")
        
        drama_trans = 0
        drama_skip = 0

        for ep in ep_keys:
            out_path = os.path.join(out_dir, f"{ep}_es.vtt")
            # If already exists and is non-empty, skip
            if os.path.exists(out_path) and os.path.getsize(out_path) > 50:
                drama_skip += 1
                total_skipped_eps += 1
                continue
                
            ep_sub = subs[ep]
            # Find English sub URL
            en_info = ep_sub.get('en') if isinstance(ep_sub, dict) else None
            en_url = en_info.get('url') if isinstance(en_info, dict) else en_info
            
            if not en_url:
                # If there's any other subtitle URL, use it
                for k, v in (ep_sub if isinstance(ep_sub, dict) else {}).items():
                    if k != 'es':
                        en_url = v.get('url') if isinstance(v, dict) else v
                        break

            if not en_url:
                continue

            try:
                req = urllib.request.Request(en_url, headers=HEADERS)
                raw_en = urllib.request.urlopen(req, timeout=12).read().decode('utf-8', 'ignore')
                es_vtt = translate_srt_to_es(raw_en)
                
                with open(out_path, 'w', encoding='utf-8') as sf:
                    sf.write(es_vtt)
                    
                drama_trans += 1
                total_translated_eps += 1
                if drama_trans % 10 == 0 or drama_trans == len(ep_keys):
                    print(f"   -> Translated {drama_trans}/{len(ep_keys)} eps...")
            except Exception as e:
                print(f"   [!] Error translating {slug} ep {ep}: {e}")

            time.sleep(0.12) # Safe pacing to prevent throttling

        print(f"   [OK] Finished: {drama_trans} translated, {drama_skip} already cached.\n")

    print("============================================================")
    print(f"BATCH TRANSLATION COMPLETED SUCCESSFULLY!")
    print(f"Total episodes newly translated: {total_translated_eps}")
    print(f"Total episodes skipped (already had Spanish subs): {total_skipped_eps}")
    print("============================================================")

if __name__ == '__main__':
    process_all_subtitles()
