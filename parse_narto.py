import glob
import re

for fname in glob.glob('_narto_script_*.txt'):
    with open(fname, encoding='utf-8', errors='ignore') as f:
        t = f.read()
    apis = re.findall(r'[\'\"`](/api/[^\'\"`\s]+)[\'\"`]', t)
    urls = re.findall(r'https?://[^\s\'\"`<>]+', t)
    print(f"{fname} (len: {len(t)}):")
    if apis:
        print("  APIs:", set(apis))
    for u in set(urls):
        if any(w in u.lower() for w in ['stream', 'play', 'video', 'dramabox', 'media', 'token', 'ticket']):
            print("  URL:", u[:120])
