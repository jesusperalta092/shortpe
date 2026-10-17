import requests
import re
import json

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
url = "https://www.kurzdrama.com/es/episodes/episode-1-the-alphas-forbidden-bunny-6ab397e13282a14d03058cf7-vh535sk0vc"
r = requests.get(url, headers={'User-Agent': UA}, timeout=10)

# Check subtitles or language metadata in the page
vtts = re.findall(r'https?://[^\s"\'<>]+\.vtt[^\s"\'<>]*', r.text)
srts = re.findall(r'https?://[^\s"\'<>]+\.srt[^\s"\'<>]*', r.text)
print("vtts:", vtts)
print("srts:", srts)
# Search for language or subtitle keys in html
print("subtitle references:", re.findall(r'["\']?(?:subtitle|caption|lang|language)["\']?:\s*["\']?([^"\',}]+)', r.text, re.I)[:10])
