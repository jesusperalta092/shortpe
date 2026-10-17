import urllib.request
import re
import json
import xml.etree.ElementTree as ET
import sys

sys.stdout.reconfigure(encoding='utf-8')
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'

# 1. Inspect kurzdrama.com/robots.txt
print("=== 1. kurzdrama robots.txt ===")
try:
    req = urllib.request.Request('https://www.kurzdrama.com/robots.txt', headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=10) as r:
        txt = r.read().decode('utf-8', errors='ignore')
        print(txt)
except Exception as e:
    print("robots.txt error:", e)

# 2. Inspect kurzdrama.com sitemap and all sub-sitemaps
print("\n=== 2. kurzdrama sitemaps ===")
sitemaps = ['https://www.kurzdrama.com/sitemap.xml']
all_es_urls = set()
for sm in sitemaps:
    try:
        req = urllib.request.Request(sm, headers={'User-Agent': UA})
        with urllib.request.urlopen(req, timeout=10) as r:
            content = r.read()
            root = ET.fromstring(content)
            for loc in root.iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc'):
                url = loc.text.strip()
                if url.endswith('.xml'):
                    if url not in sitemaps:
                        sitemaps.append(url)
                elif '/es/' in url:
                    all_es_urls.add(url)
    except Exception as e:
        print(f"Error reading sitemap {sm}:", e)

print(f"Total sitemaps found: {len(sitemaps)}")
for sm in sitemaps:
    print(" ", sm)
print(f"Total /es/ URLs in sitemaps: {len(all_es_urls)}")

# 3. Check ReelShort Spanish sitemaps & API (KurzDrama is a front for ReelShort)
print("\n=== 3. ReelShort sitemaps ===")
rs_sitemaps = ['https://www.reelshort.com/sitemap.xml']
rs_es_urls = set()
for sm in rs_sitemaps:
    try:
        req = urllib.request.Request(sm, headers={'User-Agent': UA})
        with urllib.request.urlopen(req, timeout=10) as r:
            root = ET.fromstring(r.read())
            for loc in root.iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc'):
                url = loc.text.strip()
                if url.endswith('.xml'):
                    if url not in rs_sitemaps:
                        rs_sitemaps.append(url)
                elif '/es/' in url:
                    rs_es_urls.add(url)
    except Exception as e:
        print(f"Error reading RS sitemap {sm}:", e)

print(f"ReelShort sitemaps: {len(rs_sitemaps)}")
for sm in rs_sitemaps:
    print(" ", sm)
print(f"Total Reelshort /es/ URLs: {len(rs_es_urls)}")
