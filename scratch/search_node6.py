import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('scratch/node6.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Look for next episode, previous episode, or episode list
matches = re.findall(r'[a-zA-Z0-9_]+\.(?:next|prev|episode|chapter|list|episodes|chapters)[a-zA-Z0-9_]*', js)
print("Matches sample:", set(matches))

# Look for all functions or handlers in node 6
print("\nSnippets with 'episode' or 'm3u8':")
for m in re.finditer(r'(?:episode|m3u8|chapter|next)', js, re.I):
    start = max(0, m.start() - 60)
    end = min(len(js), m.end() + 80)
    print("---", js[start:end])
