import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('scratch/kurz_parsed_home.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print("Raw shelves in scratch/kurz_parsed_home.json:")
for sh_name, items in data['shelves'].items():
    print(f"  {sh_name}: {len(items)} items")
