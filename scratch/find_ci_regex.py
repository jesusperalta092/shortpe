import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('scratch/node6.js', 'r', encoding='utf-8') as f:
    js = f.read()

import re
m = re.search(r'function\s+Ci\([^)]*\)\s*\{[^}]*\}', js)
if m:
    print("Found Ci:", m.group(0))
else:
    # search any definition of Ci
    m2 = re.search(r'Ci\s*=\s*[^,;]+', js)
    if m2:
        print("Found Ci=:", m2.group(0))
    else:
        print("Not found with simple regex")
