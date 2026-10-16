import json, re

hd = json.load(open('data/hotdrama.json', encoding='utf-8'))

def clean_item(d):
    it = dict(d)
    it.pop('episodes', None)
    it.pop('episode_hashes', None)
    it.pop('subtitles', None)
    return it

def match_drama(d, kws):
    t = d.get('title', '').lower()
    desc = d.get('description', '').lower()
    return any(k.lower() in t or k.lower() in desc for k in kws)

shelves_def = [
    {
        'name': 'Top Tendencias',
        'icon': '🔥',
        'filter': lambda d: True,
        'sort': lambda d: -(d.get('total_episodes') or 0)
    },
    {
        'name': 'Romance CEO & Millonarios',
        'icon': '💍',
        'filter': lambda d: match_drama(d, ['ceo', 'jefa', 'jefe', 'chambear', 'heredero', 'millonario', 'magnate', 'esposo', 'esposa', 'matrimonio', 'oro'])
    },
    {
        'name': 'Fantasía, Poder & Dioses',
        'icon': '⚡',
        'filter': lambda d: match_drama(d, ['dios', 'bestia', 'mago', 'místico', 'invencible', 'supremo', 'inmortal', 'lobo', 'dragón', 'fuego', 'hielo', 'luz'])
    },
    {
        'name': 'Amor, Pasión & Destino',
        'icon': '💋',
        'filter': lambda d: match_drama(d, ['amor', 'beso', 'cicatrices', 'florecimiento', 'amarnos', 'pasión', 'estrella', 'chica', 'mimada', 'mami'])
    },
    {
        'name': 'Venganza & Renacimiento',
        'icon': '👑',
        'filter': lambda d: match_drama(d, ['fatalidad', 'venganza', 'renacido', 'karma', 'robadas', 'despertar', 'retiré', 'ruido', 'enemiga', 'desterrada'])
    },
    {
        'name': 'Catálogo HotDrama Doblado',
        'icon': '🎙️',
        'filter': lambda d: True
    }
]

out_shelves = []
for s in shelves_def:
    matched = [clean_item(d) for d in hd if s['filter'](d)]
    if 'sort' in s:
        matched.sort(key=s['sort'])
    out_shelves.append({
        'name': s['name'],
        'icon': s['icon'],
        'count': len(matched),
        'items': matched[:10],
        'all_items': matched
    })

data = {'shelves': out_shelves}
with open('data/hotdrama_shelves.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Generado data/hotdrama_shelves.json con {len(out_shelves)} categorias:")
for s in out_shelves:
    print(f" - {s['name']}: {s['count']} titulos")

