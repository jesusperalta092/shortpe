import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('scratch/node6.js', 'r', encoding='utf-8') as f:
    js = f.read()

import re
matches = re.findall(r'[a-zA-Z0-9_$]+\s*=\s*function\s+Ci|function\s+Ci\b|[a-zA-Z0-9_$]+\s*=\s*\([^)]*\)\s*=>\s*[^;]+|const\s+Ci\b|let\s+Ci\b|var\s+Ci\b', js)
print("Matches:", matches[:10])

# Let's search where Ci( is used
calls = [m.start() for m in re.finditer(r'\bCi\(', js)]
print("Calls to Ci:", len(calls))
for p in calls:
    print("---", js[max(0, p-60):min(len(js), p+120)])
