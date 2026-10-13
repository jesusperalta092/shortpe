import json, sys

sys.stdout.reconfigure(encoding='utf-8')
hd = json.load(open('data/hotdrama.json', encoding='utf-8'))
print(f"Total HotDrama: {len(hd)}")
for i, d in enumerate(hd):
    print(f"{i+1:3d}. {d.get('title')}")
