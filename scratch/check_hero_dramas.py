import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('data/dramatube.json', 'r', encoding='utf-8') as f:
    dramas = json.load(f)

for d in dramas[:6]:
    print("Title:", d.get('title'))
    print("Poster:", d.get('poster'))
    print("Eps:", d.get('total_episodes'))
    print("Slug:", d.get('slug'))
    print("---")
