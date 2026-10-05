import json, os

data_path = 'data/dramatube.json'
catalog = json.load(open(data_path, encoding='utf-8'))

ai_posters = {
    'dt-the-stand-in-bride-refusal': 'posters/dt/dt-the-stand-in-bride-refusal.jpg',
    'dt-my-mafia-husband-doesnt-know-i-speak-italian': 'posters/dt/dt-my-mafia-husband-doesnt-know-i-speak-italian.jpg',
    'dt-bound-to-the-mob-alphas-baby': 'posters/dt/dt-bound-to-the-mob-alphas-baby.jpg'
}

for item in catalog:
    slug = item.get('slug')
    if slug in ai_posters:
        local_rel = ai_posters[slug]
        item['poster_local'] = local_rel
        item['poster'] = '/' + local_rel
        print(f"Set {item.get('title')} poster to /{local_rel}")

with open(data_path, 'w', encoding='utf-8') as f:
    json.dump(catalog, f, ensure_ascii=False, indent=2)

print("Saved updated data/dramatube.json!")
