import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('scratch/svelte_ep.js', 'r', encoding='utf-8') as f:
    content = f.read()

print("File size:", len(content))
print("--- START ---")
print(content[:2000])
print("--- END ---")
print(content[-2000:])
