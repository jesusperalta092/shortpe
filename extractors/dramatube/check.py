import json, os

p = 'data/dramatube.json'
if os.path.exists(p):
    d = json.load(open(p, encoding='utf-8'))
    print(f"Total dramas in data/dramatube.json: {len(d)}")
    for i, x in enumerate(d, 1):
        print(f"  {i}. {x.get('title')} ({x.get('total_episodes')} eps)")
else:
    print("File does not exist")
