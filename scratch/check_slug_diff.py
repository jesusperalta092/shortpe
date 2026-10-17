import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('scratch/kurz_parsed_home.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for d in data['dramas']:
    if 'esposo falso' in d.get('title', '').lower() or 'mentiras' in d.get('title', '').lower():
        print(d.get('title'), "->", d.get('href'))
