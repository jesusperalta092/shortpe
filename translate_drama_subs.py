import urllib.request
import urllib.parse
import json
import re
import os
import time

def wrap_subtitle_text(text, max_len=52):
    """Formats subtitle lines naturally: keeps single sentences together (up to 52 chars) and splits only long sentences."""
    if not text:
        return ""
    # Normalize multiple whitespaces and newlines
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
            # Convert timestamp from SRT (,) to VTT (.)
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
    
    url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=es&dt=t&q={urllib.parse.quote(combined_text)}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    res = urllib.request.urlopen(req, timeout=15)
    data = json.loads(res.read().decode('utf-8'))
    translated_full = ''.join([part[0] for part in data[0] if part[0]])
    
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

def translate_drama(slug, max_eps=5):
    with open('data/dramatube.json', 'r', encoding='utf-8') as f:
        catalog = json.load(f)
        
    drama = next((d for d in catalog if d.get('slug') == slug), None)
    if not drama:
        print(f"Drama {slug} not found in dramatube.json")
        return
        
    subs = drama.get('subtitles', {})
    print(f"Translating subtitles for: {drama.get('title')} ({len(subs)} episodes)...")
    
    out_dir = os.path.join('data', 'subtitles', slug)
    os.makedirs(out_dir, exist_ok=True)
    
    ep_keys = sorted(subs.keys(), key=lambda x: int(x) if x.isdigit() else 999)
    if max_eps:
        ep_keys = ep_keys[:max_eps]
        
    for ep in ep_keys:
        ep_sub = subs[ep]
        en_info = ep_sub.get('en') if isinstance(ep_sub, dict) else None
        en_url = en_info.get('url') if isinstance(en_info, dict) else en_info
        
        if not en_url:
            print(f"Ep {ep}: No English subtitle URL")
            continue
            
        try:
            req = urllib.request.Request(en_url, headers={'User-Agent': 'Mozilla/5.0'})
            raw_en = urllib.request.urlopen(req, timeout=12).read().decode('utf-8', 'ignore')
            
            es_vtt = translate_srt_to_es(raw_en)
            out_path = os.path.join(out_dir, f"{ep}_es.vtt")
            with open(out_path, 'w', encoding='utf-8') as sf:
                sf.write(es_vtt)
                
            print(f"Ep {int(ep):02d}: OK -> Saved {out_path} ({len(es_vtt)} bytes)")
        except Exception as e:
            print(f"Ep {ep}: Error {e}")
        time.sleep(0.1)

if __name__ == '__main__':
    # Test on Pregnant by the Wrong Twin (first 5 episodes)
    translate_drama('dt-pregnant-by-the-wrong-twin', max_eps=5)
