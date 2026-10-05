import json
import requests
import re
import os
import sys
from bs4 import BeautifulSoup

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace', line_buffering=True)
except Exception:
    pass

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
}

with open('data/discovered_dramaexpress_slugs.json', 'r', encoding='utf-8') as f:
    slugs = json.load(f)

print(f"Total discovered slugs: {len(slugs)}")

working = []
for idx, s in enumerate(slugs[:30], 1):
    url = f"https://dramaexpress.net/series/{s}/episode-1"
    try:
        r = requests.get(url, headers=HEADERS, timeout=8)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            raw_title = soup.title.string if soup.title else s
            title = raw_title.split(' Episode 1')[0].split(' - Watch')[0].split(' | DramaExpress')[0].strip()
            
            book_id_match = re.search(r'bookId[\\"]*:\s*[\\"]*([a-zA-Z0-9_-]+)', r.text)
            book_id = book_id_match.group(1) if book_id_match else None
            
            ep_numbers = [int(x) for x in re.findall(r'serial_number[\\"]*:\s*(\d+)', r.text)]
            total_eps = max(ep_numbers) if ep_numbers else 0
            
            print(f"[{idx}] '{title}' ({s}) -> BookID: {book_id} | TotalEps: {total_eps}")
            if book_id and total_eps > 0:
                working.append({'slug': s, 'title': title, 'bookId': book_id, 'total_eps': total_eps})
        else:
            print(f"[{idx}] {s} -> status {r.status_code}")
    except Exception as e:
        print(f"[{idx}] {s} -> error {e}")

print(f"\n[SUMMARY] Successfully validated {len(working)}/30 dramas with complete BookID and Episodes!")
