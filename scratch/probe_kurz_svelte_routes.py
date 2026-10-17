import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('scratch/kurz_home_raw.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Search for routes definition in SvelteKit
m = re.search(r'kit\.start\([^)]+\)', html)
if m:
    print("kit.start match:", m.group(0)[:500])

# Find all node chunk references in html
nodes = re.findall(r'nodes/(\d+)\.([a-zA-Z0-9_-]+)\.js', html)
print(f"Nodes referenced: {nodes}")

# Also search for all route paths
routes = re.findall(r'\[\s*(\d+)\s*,\s*\"([^\"]+)\"', html)
print(f"Routes: {routes[:20]}")
