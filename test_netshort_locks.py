import requests, re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
}

slug_id = 'claimed-by-three-alphas-2105968477965524993'

for ep in [6, 7, 8, 9, 10, 11, 12]:
    url = f'https://netshort.com/episode/{slug_id}-ep-{ep}'
    r = requests.get(url, headers=headers, timeout=15)
    chunks = re.findall(r'self\.__next_f\.push\(\[1,"(.+?)"\]\)', r.text)
    rsc = ''.join(chunks).encode().decode('unicode_escape', errors='ignore')
    vm = re.search(r'"playVoucher":"([^"]+)"', rsc)
    # Check if there is lock / isLock / isFree / playAuth / videoId
    locks = re.findall(r'"(isLock|lock|isFree|price|coin|vip|unlock)"\s*:\s*([^,}]+)', rsc)
    print(f"Ep {ep}: Video found = {bool(vm)} | locks/pricing: {locks}")
    if not vm:
        # Check what video properties exist in rsc
        vprops = re.findall(r'"([a-zA-Z0-9_]*video[a-zA-Z0-9_]*)"\s*:\s*"?([^",}]+)"?', rsc, re.IGNORECASE)
        print(f"   Video props on ep {ep}:", vprops[:5])
