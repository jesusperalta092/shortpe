import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('scratch/kurz_ep_raw.html', 'r', encoding='utf-8') as f:
    html = f.read()

scripts = re.findall(r'import\("([^"]+)"\)', html)
print("Imported scripts:", scripts)

links = re.findall(r'<link[^>]+href="([^"]+)"', html)
print("Linked resources:", links)
