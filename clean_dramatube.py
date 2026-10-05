import json

TITLE_MAP = {
    'dt-craving-the-wrong-brother-2': 'Craving the Wrong Brother',
    'dt-kneel-thunder-queen-returns': 'Kneel, Thunder Queen Returns',
    'dt-pregnant-by-the-wrong-twin': 'Pregnant by the Wrong Twin',
    'dt-they-bullied-a-vegetarian-but-i-m-a-vampire': "They Bullied a Vegetarian, But I'm a Vampire",
    'dt-the-stand-in-bride-refusal': 'The Stand-In Bride Refusal',
    'dt-my-mafia-husband-doesnt-know-i-speak-italian': "My Mafia Husband Doesn't Know I Speak Italian",
    'dt-beg-the-wife-you-threw-away': 'Beg the Wife You Threw Away',
    'dt-my-stepsons-obsession-after-my-husbands-death': "My Stepson's Obsession After My Husband's Death",
    'dt-bound-to-the-mob-alphas-baby': "Bound to the Mob Alpha's Baby",
    'dt-the-mafia-dons-royal-husband': "The Mafia Don's Royal Husband"
}

d = json.load(open('data/dramatube.json', encoding='utf-8'))
for item in d:
    slug = item.get('slug')
    if slug in TITLE_MAP:
        item['title'] = TITLE_MAP[slug]
    print(f"- {item['title']}: {item['total_episodes']} episodios ({item['slug']})")

with open('data/dramatube.json', 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False, indent=2)

print(f"\n[OK] data/dramatube.json limpiado correctamente con {len(d)} dramas!")
