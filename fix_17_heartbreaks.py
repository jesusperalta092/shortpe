import json
import requests
import os
import re
import base64
import urllib.parse
import urllib.request
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace', line_buffering=True)
except Exception:
    pass

def resolve_url(url):
    if not url:
        return url
    if '/e/s/' in url:
        try:
            jwt_part = url.split('/e/s/')[1].split('.')[0]
            padding = '=' * (-len(jwt_part) % 4)
            decoded = json.loads(base64.urlsafe_b64decode(jwt_part + padding))
            if 'src' in decoded:
                return decoded['src']
        except Exception:
            pass
    return url

def wrap_subtitle_text(text, max_len=52):
    if not text:
        return ""
    single_line = ' '.join(text.strip().split())
    if len(single_line) <= max_len:
        return single_line
    words = single_line.split()
    lines, curr, curr_len = [], [], 0
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
    blocks = [b.strip() for b in re.split(r'\n\s*\n', srt_content.strip()) if b.strip()]
    parsed, dialogues = [], []
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
        return 'WEBVTT\n\n'
    delimiter = '\n[[[---]]]\n'
    combined_text = delimiter.join(dialogues)
    url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=es&dt=t&q={urllib.parse.quote(combined_text)}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    res = urllib.request.urlopen(req, timeout=15)
    data = json.loads(res.read().decode('utf-8'))
    translated_full = ''.join([part[0] for part in data[0] if part[0]])
    translated_dialogues = re.split(r'\s*\[\[\[---\]\]\]\s*', translated_full)
    out_lines = ['WEBVTT\n']
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

slug = 'dt-17-heartbreaks-when-love-has-no-voice'
out_dir = os.path.join('data', 'subtitles', slug)
os.makedirs(out_dir, exist_ok=True)

with open('data/dramatube.json', 'r', encoding='utf-8') as f:
    d = json.load(f)
item = next((x for x in d if x.get('slug') == slug), None)
subs = item.get('subtitles', {})

print(f"Translating all {len(subs)} episodes for 17 Heartbreaks...")
success = 0
for ep_k, sub_info in subs.items():
    raw_url = sub_info.get('en', {}).get('url') if isinstance(sub_info.get('en'), dict) else sub_info.get('en')
    direct = resolve_url(raw_url)
    out_file = os.path.join(out_dir, f"{ep_k}_es.vtt")
    try:
        r = requests.get(direct, headers={'User-Agent': 'Mozilla/5.0'}, timeout=8)
        if r.status_code == 200 and r.text.strip():
            vtt = translate_srt_to_es(r.text)
            with open(out_file, 'w', encoding='utf-8') as f:
                f.write(vtt)
            success += 1
            if int(ep_k) % 15 == 0 or int(ep_k) == len(subs):
                print(f"  [OK] Ep {ep_k}/{len(subs)} translated!")
    except Exception as e:
        print(f"  [ERR] Ep {ep_k}: {e}")

print(f"🎉 COMPLETADO: {success}/{len(subs)} subtítulos traducidos para '{item.get('title')}'!")
