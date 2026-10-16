import json, os, urllib.request

r = urllib.request.urlopen('http://127.0.0.1:8090/api/catalog')
cat = json.loads(r.read())

drama_items = [d for d in cat if d.get('section') == 'drama']
shorts_items = [d for d in cat if d.get('section') == 'dramashorts']

def clean_item(d):
    it = dict(d)
    it.pop('episodes', None)
    it.pop('episode_hashes', None)
    it.pop('subtitles', None)
    return it

def match_drama(d, keywords, genres):
    d_genres = [g.lower() for g in d.get('genres', [])]
    t = d.get('title', '').lower()
    for g in genres:
        if g.lower() in d_genres: return True
    for kw in keywords:
        if kw.lower() in t: return True
    return False

# 1. GENERATE DRAMAS SHELVES
dramas_shelves_def = [
    {'name': 'Top Tendencias', 'icon': '🔥', 'filter': lambda d: True, 'sort': lambda d: -(d.get('total_episodes') or 0)},
    {'name': 'Romance Apasionado', 'icon': '❤️', 'filter': lambda d: match_drama(d, ['amor', 'boda', 'casar', 'enamor', 'beso', 'novi', 'esposo', 'esposa', 'prometido'], ['Romance'])},
    {'name': 'Realeza & Alta Sociedad', 'icon': '👑', 'filter': lambda d: match_drama(d, ['reina', 'rey', 'princesa', 'principe', 'trono', 'imperio', 'noble', 'palacio'], ['Realeza'])},
    {'name': 'Billonarios & CEOs', 'icon': '💼', 'filter': lambda d: match_drama(d, ['ceo', 'billonario', 'millonario', 'magnate', 'jefe', 'rico', 'heredero'], ['Billonario'])},
    {'name': 'Hombres Lobo & Vampiros', 'icon': '🐺', 'filter': lambda d: match_drama(d, ['lobo', 'vampiro', 'alfa', 'luna', 'licantropo'], ['Werewolf', 'Vampiro', 'Criaturas'])},
    {'name': 'Fantasía & Dragones', 'icon': '🐉', 'filter': lambda d: match_drama(d, ['dragon', 'magia', 'inmortal', 'dios', 'celestial', 'cultivo'], ['Dragón', 'Fantasía'])},
    {'name': 'Venganza & Renacimiento', 'icon': '🗡️', 'filter': lambda d: match_drama(d, ['renacer', 'renacido', 'venganza', 'traicion', 'volver', 'revancha'], ['Renacimiento', 'Venganza', 'Mafia'])},
    {'name': 'Misterio & Identidad Oculta', 'icon': '🎭', 'filter': lambda d: match_drama(d, ['secreto', 'oculto', 'misterio', 'identidad', 'enmascarado', 'disfraz'], ['Misterio'])},
    {'name': 'Familia & Destino', 'icon': '👨‍👩‍👧', 'filter': lambda d: match_drama(d, ['hijo', 'hija', 'padre', 'madre', 'hermano', 'mama', 'papa', 'abuelo'], ['Familia'])},
    {'name': 'Militar & Poder Supremo', 'icon': '⚡', 'filter': lambda d: match_drama(d, ['general', 'militar', 'soldado', 'mariscal', 'guerra', 'comandante', 'as'], ['Militar'])}
]

dramas_shelves = []
for s in dramas_shelves_def:
    matched = [clean_item(d) for d in drama_items if s['filter'](d)]
    if 'sort' in s:
        matched.sort(key=s['sort'])
    dramas_shelves.append({
        'name': s['name'],
        'icon': s['icon'],
        'count': len(matched),
        'items': matched[:10],
        'all_items': matched
    })

with open('data/dramas_shelves.json', 'w', encoding='utf-8') as f:
    json.dump({'shelves': dramas_shelves}, f, ensure_ascii=False, indent=2)

# 2. GENERATE DRAMASHORTS SHELVES
shorts_shelves_def = [
    {'name': 'Estrenos Exclusivos', 'icon': '⚡', 'filter': lambda d: True, 'sort': lambda d: -(d.get('total_episodes') or 0)},
    {'name': 'Romance & Pasión', 'icon': '❤️', 'filter': lambda d: match_drama(d, ['amor', 'boda', 'casar', 'enamor', 'beso', 'novi', 'novia', 'esposo', 'esposa', 'pareja'], ['Romance'])},
    {'name': 'CEO & Alta Sociedad', 'icon': '💼', 'filter': lambda d: match_drama(d, ['ceo', 'millonario', 'billonario', 'magnate', 'jefe', 'rico', 'heredera', 'patron'], ['CEO'])},
    {'name': 'Mafia & Poder Oscuro', 'icon': '🔫', 'filter': lambda d: match_drama(d, ['mafia', 'mafiosa', 'mafioso', 'gangster', 'jefe', 'cartel', 'crimen'], ['Mafia'])},
    {'name': 'Venganza & Traición', 'icon': '🗡️', 'filter': lambda d: match_drama(d, ['venganza', 'renacida', 'renacer', 'traicion', 'vengar', 'odio', 'revancha'], ['Venganza'])},
    {'name': 'Fantasía & Misterio', 'icon': '🔮', 'filter': lambda d: match_drama(d, ['fantasia', 'magia', 'lobo', 'misterio', 'secreto', 'poder', 'sobrenatural'], ['Fantasía', 'Misterio'])},
    {'name': 'Drama & Secretos', 'icon': '🎭', 'filter': lambda d: match_drama(d, ['secreto', 'engaño', 'mentira', 'verdad', 'oculto'], ['Drama'])},
    {'name': 'Todos los DramaShorts', 'icon': '💎', 'filter': lambda d: True}
]

shorts_shelves = []
for s in shorts_shelves_def:
    matched = [clean_item(d) for d in shorts_items if s['filter'](d)]
    if 'sort' in s:
        matched.sort(key=s['sort'])
    shorts_shelves.append({
        'name': s['name'],
        'icon': s['icon'],
        'count': len(matched),
        'items': matched[:10],
        'all_items': matched
    })

with open('data/dramashorts_shelves.json', 'w', encoding='utf-8') as f:
    json.dump({'shelves': shorts_shelves}, f, ensure_ascii=False, indent=2)

print("ARCHIVOS GENERADOS EXITOSAMENTE:")
print(" - data/dramas_shelves.json con", len(dramas_shelves), "estantes")
print(" - data/dramashorts_shelves.json con", len(shorts_shelves), "estantes")
