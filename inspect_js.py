import requests
import re

for js in ['1kz2_c1i-fvej.js', '0b-fbx02n9frn.js', '36p-r21d532d3.js', '1orf84ueak1ie.js']:
    url = f'https://dramix.tv/_next/static/chunks/{js}'
    r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    t = r.text
    api_calls = re.findall(r'["\'`](/api/[^"\'`\s]+)["\'`]', t)
    print(f"=== {js} (status {r.status_code}, len {len(t)}) ===")
    print("API routes:", set(api_calls))
    for m in re.finditer(r'(fetch\([^)]+\))', t):
        snippet = m.group(1)[:120]
        if 'api' in snippet or 'drama' in snippet or 'play' in snippet or 'video' in snippet:
            print("  fetch:", snippet)
