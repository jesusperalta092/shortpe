import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('scratch/node6.js', 'r', encoding='utf-8') as f:
    js = f.read()

import re
matches = [m.start() for m in re.finditer(r'Se\(', js)]
print("Se( occurrences:", len(matches))
for pos in matches:
    print("---", js[max(0, pos-150):min(len(js), pos+250)])
