import requests
import re

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
url = "https://www.kurzdrama.com/es/episodes/episode-1-tras-renacer-me-cas%C3%A9-con-el-hermano-de-mi-prometido-6acefab3c40611e81306e645-0hjil0mzy2"
r = requests.get(url, headers={'User-Agent': UA}, timeout=10)
print("Known ES drama:", r.status_code)
# Look for video or m3u8
m3u8s = re.findall(r'https?://[^\s"\'<>]+\.m3u8[^\s"\'<>]*', r.text)
print("m3u8s found:", len(m3u8s))
mp4s = re.findall(r'https?://[^\s"\'<>]+\.mp4[^\s"\'<>]*', r.text)
print("mp4s found:", len(mp4s))
if m3u8s:
    print("Sample m3u8:", m3u8s[0])
elif mp4s:
    print("Sample mp4:", mp4s[0])
