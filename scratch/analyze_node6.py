import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('scratch/node6.js', 'r', encoding='utf-8') as f:
    js = f.read()

print(f"Length of node6.js: {len(js)}")
matches = set(re.findall(r'(?:https?://[^"\'\s<>]+|/api/[^"\'\s<>]+)', js))
for m in sorted(matches):
    print("Match:", m)

# Also let's inspect functions related to episode loading
for f_match in re.finditer(r'(function\s+[a-zA-Z0-9_$]+\s*\([^)]*\)\s*\{[^}]{1,300}\})', js):
    snippet = f_match.group(1)
    if 'episode' in snippet.lower() or 'reelshort' in snippet.lower() or 'm3u8' in snippet.lower() or 'proxy' in snippet.lower():
        print("--- Function snippet ---")
        print(snippet[:200])
