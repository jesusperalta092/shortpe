import requests
from bs4 import BeautifulSoup
import sys

sys.stdout.reconfigure(encoding='utf-8')
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
url = "https://www.kurzdrama.com/es/episodes/episode-1-the-alphas-forbidden-bunny-6ab397e13282a14d03058cf7-vh535sk0vc"
r = requests.get(url, headers={'User-Agent': UA}, timeout=10)
soup = BeautifulSoup(r.text, 'html.parser')
title = soup.title.text if soup.title else ''
print("Title:", title)
print("Page contains 'Not Found' or 404:", '404' in r.text or 'Not Found' in r.text)
# Look for video or m3u8 or bookId
import re
print("Found video streams or book_id:", re.findall(r'book_id["\']?:\s*["\']([a-f0-9]+)["\']', r.text))
