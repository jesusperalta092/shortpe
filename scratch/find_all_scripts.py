import re

with open('scratch/kurz_home_raw.html', 'r', encoding='utf-8') as f:
    html = f.read()

scripts = re.findall(r'src=["\']([^"\']+\.js)["\']', html)
print(f"Scripts in HTML: {len(scripts)}")
for s in scripts:
    print(" ", s)
