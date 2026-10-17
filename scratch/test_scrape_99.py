import requests
import re
from bs4 import BeautifulSoup
import sys

sys.stdout.reconfigure(encoding='utf-8')
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

# Try different book_slugs for "99 oportunidades"
book_slugs_to_try = [
    '99-oportunidades-un-adiÃ³s-6a55969fc113bc78b30961f2',
    '99-oportunidades-un-adios-6a55969fc113bc78b30961f2',
    '99-oportunidades-un-adi%C3%B3s-6a55969fc113bc78b30961f2'
]

for bs in book_slugs_to_try:
    url = f"https://www.reelshort.com/es/full-episodes/{bs}"
    r = requests.get(url, headers={'User-Agent': UA}, timeout=10)
    print(f"URL: {url}")
    print(f"  status: {r.status_code}, len: {len(r.text)}")
    eps = re.findall(r'/episodes/([^"\'\s>]+)', r.text)
    print(f"  episodes found: {len(eps)}")
    if eps:
        print("  sample ep:", eps[0])
