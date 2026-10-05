import requests, re

js = requests.get('https://netshort.com/_next/static/chunks/8000-e7b841909b9e1a44.js', headers={'User-Agent': 'Mozilla/5.0'}).text

# Find all calls to U("/...") or request("/...") or post("/...")
matches = re.findall(r'(\w+)\s*\(\s*["\'](/[^"\']+)["\']', js)
print("Function calls with API paths:")
for fn, path in set(matches):
    print(f"  {fn}('{path}')")
