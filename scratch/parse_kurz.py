
import re, json

with open('scratch/kurz_ep_raw.html', 'r', encoding='utf-8') as f:
    text = f.read()

print('Title:', re.findall(r'<title>(.*?)</title>', text, re.I))
print('Videos:', re.findall(r'<video[^>]*>', text, re.I))
print('Sources:', re.findall(r'<source[^>]*>', text, re.I))

# Check script tags
scripts = re.findall(r'<script([^>]*)>(.*?)</script>', text, re.S)
print('Total scripts:', len(scripts))
for i, (attrs, body) in enumerate(scripts):
    body_clean = body.strip()
    if 'src=' in attrs:
        print(f'Script {i} src:', attrs)
    elif len(body_clean) > 0:
        keywords = ['m3u8', 'mp4', 'stream', 'episode', 'video', 'player', 'kurz']
        found = [k for k in keywords if k in body_clean.lower()]
        if found:
            print(f'Script {i} (len {len(body_clean)}) matched {found}:')
            print(body_clean[:300])
            print('---')
