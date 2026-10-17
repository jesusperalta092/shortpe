import requests
import re
import json

hdrs = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36',
    'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8'
}

# 1. Fetch Home
print("Fetching https://www.kurzdrama.com/es ...")
r_home = requests.get('https://www.kurzdrama.com/es', headers=hdrs, timeout=15)
print("Home status:", r_home.status_code, "len:", len(r_home.text))

with open('scratch/kurz_home_raw.html', 'w', encoding='utf-8') as f:
    f.write(r_home.text)

if '__NEXT_DATA__' in r_home.text:
    m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', r_home.text)
    if m:
        home_data = json.loads(m.group(1))
        with open('scratch/kurz_home_next.json', 'w', encoding='utf-8') as f:
            json.dump(home_data, f, ensure_ascii=False, indent=2)
        print("Home __NEXT_DATA__ saved.")
else:
    print("Home does NOT have __NEXT_DATA__")

# 2. Fetch Sample Episode
ep_url = 'https://www.kurzdrama.com/es/episodes/episode-1-unida-al-alfa-y-su-beta-6a433648a0263ac457025610-2az8aku8d1'
print(f"Fetching sample episode {ep_url} ...")
r_ep = requests.get(ep_url, headers=hdrs, timeout=15)
print("Ep status:", r_ep.status_code, "len:", len(r_ep.text))

with open('scratch/kurz_ep_raw.html', 'w', encoding='utf-8') as f:
    f.write(r_ep.text)

if '__NEXT_DATA__' in r_ep.text:
    m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', r_ep.text)
    if m:
        ep_data = json.loads(m.group(1))
        with open('scratch/kurz_ep_next.json', 'w', encoding='utf-8') as f:
            json.dump(ep_data, f, ensure_ascii=False, indent=2)
        print("Ep __NEXT_DATA__ saved.")
else:
    print("Ep does NOT have __NEXT_DATA__")
