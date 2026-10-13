import requests
import re
import xml.etree.ElementTree as ET

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8'
}

# 1. Check sitemap
sitemap_url = 'https://suikora.com/sitemap.xml'
try:
    r = requests.get(sitemap_url, headers=headers, timeout=10)
    print("Sitemap status:", r.status_code)
    print("Sitemap length:", len(r.text))
    with open('suikora_sitemap.xml', 'w', encoding='utf-8') as f:
        f.write(r.text)
    # Check what urls are in sitemap
    urls = re.findall(r'<loc>(.*?)</loc>', r.text)
    print(f"Total <loc> URLs in sitemap: {len(urls)}")
    for u in urls[:15]:
        print(" -", u)
except Exception as e:
    print("Sitemap error:", e)

# 2. Check home page /es/
try:
    r2 = requests.get('https://suikora.com/es', headers=headers, timeout=10)
    print("Home /es status:", r2.status_code, "Length:", len(r2.text))
    with open('suikora_home_es.html', 'w', encoding='utf-8') as f:
        f.write(r2.text)
except Exception as e:
    print("Home /es error:", e)
