import json

hd = json.load(open('data/hotdrama.json', encoding='utf-8'))
for i, d in enumerate(hd):
    t = d.get('title', '')
    eps = d.get('total_episodes', 0)
    genres = d.get('genres', [])
    desc = d.get('description', '')[:70]
    print(f"{i+1:2d}. {t} | {eps} eps | {genres} | {desc}")
