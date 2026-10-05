import shutil, os, json

os.makedirs('posters/dt', exist_ok=True)

brain_dir = r'C:\Users\USER\.gemini\antigravity-ide\brain\2d351890-1c6f-4fd8-a5bf-c7125b48c5cc'

mappings = {
    'dt-the-stand-in-bride-refusal': 'stand_in_bride_refusal_1790990356788.jpg',
    'dt-my-mafia-husband-doesnt-know-i-speak-italian': 'mafia_husband_italian_1790990419356.jpg',
    'dt-bound-to-the-mob-alphas-baby': 'bound_mob_alpha_baby_1790990468109.jpg'
}

for slug, filename in mappings.items():
    src = os.path.join(brain_dir, filename)
    dst = os.path.join('posters', 'dt', f'{slug}.jpg')
    if os.path.exists(src):
        shutil.copy2(src, dst)
        print(f"Copied {filename} to {dst}")
    else:
        print(f"Source file not found: {src}")

# Update data/dramatube.json
data_path = 'data/dramatube.json'
catalog = json.load(open(data_path, encoding='utf-8'))

for item in catalog:
    s = item.get('slug')
    if s in mappings:
        local_path = f'posters/dt/{s}.jpg'
        item['poster_local'] = local_path
        print(f"Updated {item.get('title')} with local poster {local_path}")

with open(data_path, 'w', encoding='utf-8') as f:
    json.dump(catalog, f, ensure_ascii=False, indent=2)

print("Saved data/dramatube.json successfully!")
