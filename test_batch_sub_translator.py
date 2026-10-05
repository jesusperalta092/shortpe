import urllib.request
import urllib.parse
import json
import re
import time

def batch_translate_srt(srt_content, source_lang='en', target_lang='es'):
    """Translates an entire SRT file in one single fast API call while preserving timestamps."""
    blocks = [b.strip() for b in re.split(r'\n\s*\n', srt_content.strip()) if b.strip()]
    
    parsed = []
    dialogues = []
    
    for b in blocks:
        lines = b.split('\n')
        if len(lines) >= 3 and '-->' in lines[1]:
            idx = lines[0]
            t = lines[1]
            txt = '\n'.join(lines[2:])
            parsed.append({'idx': idx, 'timestamp': t, 'has_text': True})
            dialogues.append(txt)
        elif len(lines) >= 2 and '-->' in lines[1]:
            idx = lines[0]
            t = lines[1]
            parsed.append({'idx': idx, 'timestamp': t, 'has_text': False})
        else:
            parsed.append({'raw': b, 'has_text': False})
            
    if not dialogues:
        return srt_content
        
    # Join dialogues with a safe delimiter
    delimiter = "\n[[[---]]]\n"
    combined_text = delimiter.join(dialogues)
    
    url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl={source_lang}&tl={target_lang}&dt=t&q={urllib.parse.quote(combined_text)}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    res = urllib.request.urlopen(req, timeout=15)
    data = json.loads(res.read().decode('utf-8'))
    translated_full = ''.join([part[0] for part in data[0] if part[0]])
    
    # Split back
    translated_dialogues = re.split(r'\s*\[\[\[---\]\]\]\s*', translated_full)
    
    out_blocks = []
    d_idx = 0
    for item in parsed:
        if item.get('has_text'):
            t_txt = translated_dialogues[d_idx] if d_idx < len(translated_dialogues) else dialogues[d_idx]
            d_idx += 1
            out_blocks.append(f"{item['idx']}\n{item['timestamp']}\n{t_txt}")
        elif 'idx' in item:
            out_blocks.append(f"{item['idx']}\n{item['timestamp']}")
        else:
            out_blocks.append(item.get('raw', ''))
            
    return '\n\n'.join(out_blocks)

# Let's test on full sample episode 1 of Craving the Wrong Brother
url = 'https://video-v6.mydramawave.com/vt/25200/8e1526a8-90bc-4666-b4fa-8b62625f543f.srt'
t0 = time.time()
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
raw_en = urllib.request.urlopen(req, timeout=10).read().decode('utf-8', 'ignore')

print(f"Downloaded English SRT ({len(raw_en)} bytes)...")
es_srt = batch_translate_srt(raw_en)
elapsed = time.time() - t0
print(f"Translated FULL episode to Spanish in {elapsed:.2f} seconds!")
print("\n--- FIRST 4 BLOCKS IN SPANISH ---")
print('\n\n'.join(es_srt.split('\n\n')[:4]))
