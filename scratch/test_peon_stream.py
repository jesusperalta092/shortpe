import json
import requests
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

with open('data/dramatube.json', 'r', encoding='utf-8') as f:
    dramas = json.load(f)

for d in dramas:
    if '6a8280dc24d5639f6c0666af' in d.get('slug', ''):
        print("PEON EP 1:", d.get('episodes', {}).get('1'))
        ep1_slug = d.get('episodes', {}).get('1', {}).get('slug')
        if ep1_slug:
            url = f"https://www.kurzdrama.com/es/episodes/{ep1_slug}"
            r = requests.get(url, headers={'User-Agent': UA, 'Referer': 'https://www.kurzdrama.com/'}, timeout=10)
            print(f"URL: {url} -> status {r.status_code}")
            m = re.findall(r'https?://[^\s"\'<>]+\.m3u8', r.text)
            print("m3u8 found:", m[:1])
            
    if '66e3f9dad7e22784120440cf' in d.get('slug', ''):
        print("DIOS MIO EP 1:", d.get('episodes', {}).get('1'))
        ep1_slug = d.get('episodes', {}).get('1', {}).get('slug')
        if ep1_slug:
            url = f"https://www.kurzdrama.com/es/episodes/{ep1_slug}"
            r = requests.get(url, headers={'User-Agent': UA, 'Referer': 'https://www.kurzdrama.com/'}, timeout=10)
            print(f"URL: {url} -> status {r.status_code}")
            m = re.findall(r'https?://[^\s"\'<>]+\.m3u8', r.text)
            print("m3u8 found:", m[:1])
