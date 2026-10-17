import json, requests, re, time

hd = json.load(open('data/hotdrama.json', encoding='utf-8'))
candidates = [
    'nt-doblada-dos-suenos-un-despertar',
    'nt-el-medico-divino-rodeado-de-siete-bellezas-2',
    'nt-el-ultimo-baile-por-amor',
    'nt-entre-la-niebla-y-el-viento',
    'nt-esposa-del-magnate-oculto',
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Referer': 'https://narto-drama.com/'
}

for slug in candidates:
    narto_slug = slug[3:] if slug.startswith('nt-') else slug
    url = f'https://narto-drama.com/detail/watch/{narto_slug}/1?lang=es-ES'
    try:
        r = requests.get(url, headers=headers, timeout=8)
        m = re.search(r'(https?://[^\s"\'<>]+(?:vigloo-stream|dramabox-stream|stream)[^\s"\'<>]*)', r.text)
        if m:
            stream_url = m.group(1).rstrip('`";,')
            r2 = requests.get(stream_url, headers={'User-Agent': headers['User-Agent'], 'Range': 'bytes=0-10'}, timeout=6)
            print(f"{slug} -> Stream {r2.status_code}")
        else:
            print(f"{slug} -> No stream URL (Page {r.status_code})")
    except Exception as e:
        print(f"{slug} -> Err {e}")
    time.sleep(1)
