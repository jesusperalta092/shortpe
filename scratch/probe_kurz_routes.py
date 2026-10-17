import re
import requests
from bs4 import BeautifulSoup
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('scratch/kurz_home_raw.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Find all script src
scripts = re.findall(r'<script[^>]+src=["\']([^"\']+)["\']', html)
print(f"Scripts on kurzdrama home: {len(scripts)}")
for s in scripts:
    print("  ", s)

# Find all links/hrefs in the page
hrefs = set(re.findall(r'href=["\']([^"\']+)["\']', html))
print(f"Unique hrefs on home: {len(hrefs)}")
for h in sorted(hrefs):
    if '/es/' in h:
        print("   /es/ link:", h)
