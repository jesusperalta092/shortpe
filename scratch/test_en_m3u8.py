import requests
import re

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
url = "https://www.kurzdrama.com/es/episodes/episode-1-the-alphas-forbidden-bunny-6ab397e13282a14d03058cf7-vh535sk0vc"
r = requests.get(url, headers={'User-Agent': UA}, timeout=10)
m3u8s = re.findall(r'https?://[^\s"\'<>]+\.m3u8[^\s"\'<>]*', r.text)
print("m3u8s in EN drama under /es/:", len(m3u8s))
if m3u8s:
    print("Sample m3u8:", m3u8s[0])
