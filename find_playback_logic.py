import requests
import re

url = 'https://dramix.tv/_next/static/chunks/1kz2_c1i-fvej.js'
t = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}).text

for m in re.finditer(r'(/api/playback[^\s"\'`]*)', t):
    start = max(0, m.start() - 300)
    end = min(len(t), m.end() + 400)
    print("="*40)
    print(t[start:end])
