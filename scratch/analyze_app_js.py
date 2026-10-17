import requests
import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

app_js_url = 'https://www.kurzdrama.com/_app/immutable/entry/app.ei4E-TQC.js'
r = requests.get(app_js_url, timeout=10)
print("app.js status:", r.status_code, "len:", len(r.text))

with open('scratch/app_entry.js', 'w', encoding='utf-8') as f:
    f.write(r.text)

# Look for nodes or routes mapping
routes = re.findall(r'\[\s*(\d+)\s*,\s*["\']([^"\']+)["\']', r.text)
print("Routes found:", routes)

# Look for all string literals
strings = re.findall(r'["\'](/[^"\']+)["\']', r.text)
print("Paths in app.js:", set(strings))

# Look for imports in app.js
imports = re.findall(r'import\("([^"]+)"\)', r.text)
print("Imports in app.js:", imports)
