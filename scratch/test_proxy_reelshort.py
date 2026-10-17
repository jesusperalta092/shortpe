import requests
import urllib.parse
import sys
sys.stdout.reconfigure(encoding='utf-8')

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'

reel_url = "https://www.reelshort.com/es/full-episodes/unida-al-alfa-y-su-beta-6a433648a0263ac457025610"
kurz_proxy = f"https://www.kurzdrama.com/api/proxy?url={urllib.parse.quote(reel_url)}&locale=es"

print("1. Testing kurzdrama proxy:", kurz_proxy)
try:
    r = requests.get(kurz_proxy, headers={'User-Agent': UA, 'Referer': 'https://www.kurzdrama.com/'}, timeout=10)
    print("Kurz proxy status:", r.status_code, "Length:", len(r.text))
    print("Snippet:", r.text[:300])
except Exception as e:
    print("Kurz proxy error:", e)

print("\n2. Testing direct Reelshort:", reel_url)
try:
    r2 = requests.get(reel_url, headers={'User-Agent': UA}, timeout=10)
    print("Direct Reelshort status:", r2.status_code, "Length:", len(r2.text))
    print("Snippet:", r2.text[:300])
except Exception as e:
    print("Direct Reelshort error:", e)
