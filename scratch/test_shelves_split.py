import urllib.request, json
from collections import Counter

r = urllib.request.urlopen('http://127.0.0.1:8090/api/catalog')
cat = json.loads(r.read())
drama_items = [d for d in cat if d.get('section') == 'drama']
shorts_items = [d for d in cat if d.get('section') == 'dramashorts']

def match_drama(d, keywords, genres):
    d_genres = [g.lower() for g in d.get('genres', [])]
    t = d.get('title', '').lower()
    for g in genres:
        if g.lower() in d_genres: return True
    for kw in keywords:
        if kw.lower() in t: return True
    return False

# Dramas shelves
dramas_shelves_def = [
    {'name': 'Top Tendencias', 'icon': '🔥', 'test': lambda d: True, 'sort_key': lambda d: d.get('total_episodes', 0)},
    {'name': 'Romance Apasionado', 'icon': '❤️', 'test': lambda d: match_drama(d, ['amor', 'boda', 'casar', 'enamor', 'beso', 'novi'], ['Romance'])},
    {'name': 'Realeza & Alta Sociedad', 'icon': '👑', 'test': lambda d: match_drama(d, ['reina', 'rey', 'princesa', 'principe', 'trono', 'imperio'], ['Realeza'])},
    {'name': 'Billonarios & CEOs', 'icon': '💼', 'test': lambda d: match_drama(d, ['ceo', 'billonario', 'millonario', 'magnate', 'jefe', 'rico'], ['Billonario'])},
    {'name': 'Hombres Lobo & Vampiros', 'icon': '🐺', 'test': lambda d: match_drama(d, ['lobo', 'vampiro', 'alfa', 'luna', 'licantropo'], ['Werewolf', 'Vampiro', 'Criaturas'])},
    {'name': 'Fantasía & Dragones', 'icon': '🐉', 'test': lambda d: match_drama(d, ['dragon', 'magia', 'inmortal', 'dios', 'celestial'], ['Dragón', 'Fantasía'])},
    {'name': 'Venganza & Renacimiento', 'icon': '🗡️', 'test': lambda d: match_drama(d, ['renacer', 'renacido', 'venganza', 'traicion', 'volver'], ['Renacimiento', 'Venganza', 'Mafia'])},
    {'name': 'Misterio & Suspenso', 'icon': '🎭', 'test': lambda d: match_drama(d, ['secreto', 'oculto', 'misterio', 'identidad', 'enmascarado'], ['Misterio'])},
    {'name': 'Familia & Destino', 'icon': '👨‍👩‍👧', 'test': lambda d: match_drama(d, ['hijo', 'hija', 'padre', 'madre', 'hermano', 'mama', 'papa'], ['Familia'])},
    {'name': 'Militar & Poder Supremo', 'icon': '⚡', 'test': lambda d: match_drama(d, ['general', 'militar', 'soldado', 'mariscal', 'guerra', 'comandante'], ['Militar'])}
]

print("=== DRAMAS SHELVES ===")
for s in dramas_shelves_def:
    matched = [d for d in drama_items if s['test'](d)]
    print(f"{s['icon']} {s['name']}: {len(matched)} títulos")

# DramaShorts shelves
shorts_shelves_def = [
    {'name': 'Estrenos Exclusivos', 'icon': '⚡', 'test': lambda d: True, 'sort_key': lambda d: d.get('total_episodes', 0)},
    {'name': 'Romance & Pasión', 'icon': '❤️', 'test': lambda d: match_drama(d, ['amor', 'boda', 'casar', 'enamor', 'beso', 'novi', 'novia', 'esposo', 'esposa'], ['Romance'])},
    {'name': 'CEO & Alta Sociedad', 'icon': '💼', 'test': lambda d: match_drama(d, ['ceo', 'millonario', 'billonario', 'magnate', 'jefe', 'rico', 'heredera', 'patron'], ['CEO'])},
    {'name': 'Mafia & Poder Oscuro', 'icon': '🔫', 'test': lambda d: match_drama(d, ['mafia', 'mafiosa', 'mafioso', 'gangster', 'jefe', 'cartel'], ['Mafia'])},
    {'name': 'Venganza & Traición', 'icon': '🗡️', 'test': lambda d: match_drama(d, ['venganza', 'renacida', 'renacer', 'traicion', 'vengar', 'odio'], ['Venganza'])},
    {'name': 'Fantasía & Misterio', 'icon': '🔮', 'test': lambda d: match_drama(d, ['fantasia', 'magia', 'lobo', 'misterio', 'secreto'], ['Fantasía', 'Misterio'])},
    {'name': 'Drama & Secretos', 'icon': '🎭', 'test': lambda d: match_drama(d, ['secreto', 'engaño', 'mentira', 'verdad'], ['Drama'])},
]

print("\n=== DRAMASHORTS SHELVES ===")
for s in shorts_shelves_def:
    matched = [d for d in shorts_items if s['test'](d)]
    print(f"{s['icon']} {s['name']}: {len(matched)} títulos")
