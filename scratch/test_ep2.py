import requests
import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

ep2_url = "https://www.kurzdrama.com/es/episodes/episode-2-unida-al-alfa-y-su-beta-6a433648a0263ac457025610-qrxfr6tfy4"
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
r = requests.get(ep2_url, headers={'User-Agent': UA}, timeout=10)
print("Ep 2 status:", r.status_code, "Length:", len(r.text))

m3u8_matches = re.findall(r'https?://[^\s"\'<>]+\.m3u8[^\s"\'<>]*', r.text)
print("M3u8 matches:", m3u8_matches)

# Let's also check if data contains m3u8
m = re.search(r'data:\s*(\{[^}]+\})', r.text)
if m:
    print("Data snippet:", m.group(0)[:300])

# Also check for crazymaplestudios or video URL
video_matches = re.findall(r'https?://v-mps\.crazymaplestudios\.com/[^\s"\'<>]+', r.text)
print("Video matches:", video_matches)
