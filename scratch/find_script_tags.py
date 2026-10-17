import re

with open('scratch/kurz_home_raw.html', 'r', encoding='utf-8') as f:
    html = f.read()

tags = re.findall(r'<script[^>]*>', html)
print(f"Total script tags: {len(tags)}")
for t in tags:
    print(" ", t)
