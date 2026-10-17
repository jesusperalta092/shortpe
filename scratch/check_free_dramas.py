import urllib.request
import re
from bs4 import BeautifulSoup

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
url = 'https://www.kurzdrama.com/es/free-short-dramas'
try:
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    html = urllib.request.urlopen(req, timeout=10).read().decode('utf-8', errors='ignore')
    print("Status 200, length:", len(html))
    soup = BeautifulSoup(html, 'html.parser')
    links = [a['href'] for a in soup.find_all('a', href=True) if '/episodes/' in a['href']]
    print(f"Links found in free-short-dramas: {len(links)}")
    for l in links[:10]:
        print(" ", l)
except Exception as e:
    print("Error:", e)
