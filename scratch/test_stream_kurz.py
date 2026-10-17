import requests
import sys
sys.stdout.reconfigure(encoding='utf-8')

m3u8_url = 'https://v-mps.crazymaplestudios.com/vod-112094/008e33b37c3471f181fbe7e7c4590102/e9d00c385c924001a28c0e6202ec4496-444efc5ff76307ff0d6f59de6dd07a46-sd.m3u8'
hdrs = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    'Referer': 'https://crazymaplestudios.com/'
}

r = requests.get(m3u8_url, headers=hdrs, timeout=10)
print('Direct m3u8 status:', r.status_code)
print('Content-Type:', r.headers.get('content-type'))
print('First 200 chars:\n', r.text[:200])
