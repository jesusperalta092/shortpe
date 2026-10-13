import requests
import re

url = 'https://suikora.com/es/drama/la-madrastra-que-nadie-se-atreve-a-tocar/1'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
r = requests.get(url, headers=headers)
print('Status:', r.status_code)
m3u8s = re.findall(r'https?://[^\s"\'<>]+\.m3u8[^\s"\'<>]*', r.text)
print('Total m3u8s found in page:', len(m3u8s))
if m3u8s:
    print('Sample 1:', m3u8s[0])
