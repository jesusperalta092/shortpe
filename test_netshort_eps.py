import requests, re, json

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
}

slug_id = 'claimed-by-three-alphas-2105968477965524993'

# Test various episodes: 1, 2, 5, 10, 20, 50, 95
for ep_num in [1, 2, 5, 10, 20, 50, 95]:
    # Test URL formats:
    # 1. /episode/{slug_id}-ep-{ep_num}
    # 2. /episode/{slug_id}/{ep_num}
    url = f'https://netshort.com/episode/{slug_id}-ep-{ep_num}'
    r = requests.get(url, headers=headers, timeout=15)
    
    chunks = re.findall(r'self\.__next_f\.push\(\[1,"(.+?)"\]\)', r.text)
    rsc = ''.join(chunks).encode().decode('unicode_escape', errors='ignore')
    
    vm = re.search(r'"playVoucher":"([^"]+)"', rsc)
    subs = re.findall(r'"subtitleLanguage":"([^"]+)"', rsc)
    
    video_url = vm.group(1) if vm else None
    print(f"Ep {ep_num}: Status {r.status_code} | Video found: {bool(video_url)} | Subtitles: {len(subs)} ({subs[:3]})")
    if video_url:
        print(f"   Video: {video_url[:100]}...")
