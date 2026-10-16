import json
import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

SHELF_CANONICAL = {
    'nuevos': ('Nuevos Lanzamientos', '✨'),
    'clasificacion': ('CLASIFICACIÓN', '🏆'),
    'doblada': ('Serie Doblada 📢', '📢'),
    'identidad': ('Identidad Oculta 🎭', '🎭'),
    'tabu': ('Relación Tabú', '💋'),
    'bebes': ('Bebés y Embarazos 🍼', '🍼'),
    'amor': ('Amor a Primera Vista 👄', '👄'),
    'masculino': ('Género Masculino', '⚡'),
    'lobo': ('Hombre Lobo 🐺 y Vampiro 🧛', '🐺'),
    'asia': ('Historias de Asia 🌏', '🌏'),
    'recomendados': ('Más Recomendados', '🔥'),
}

def normalize_shelf(sh):
    low = sh.lower()
    if 'nuevo' in low: return SHELF_CANONICAL['nuevos']
    if 'clasifica' in low or 'clasificaci' in low: return SHELF_CANONICAL['clasificacion']
    if 'doblada' in low: return SHELF_CANONICAL['doblada']
    if 'identidad' in low: return SHELF_CANONICAL['identidad']
    if 'tab' in low: return SHELF_CANONICAL['tabu']
    if 'beb' in low or 'embarazo' in low: return SHELF_CANONICAL['bebes']
    if 'amor' in low or 'primera vista' in low: return SHELF_CANONICAL['amor']
    if 'masculino' in low: return SHELF_CANONICAL['masculino']
    if 'lobo' in low or 'vampiro' in low: return SHELF_CANONICAL['lobo']
    if 'asia' in low: return SHELF_CANONICAL['asia']
    if 'recomenda' in low: return SHELF_CANONICAL['recomendados']
    return (sh, '🎬')

def fix_mojibake(text):
    if not text: return ''
    # Fix double-encoded UTF-8
    try:
        fixed = text.encode('latin1').decode('utf-8')
        return fixed
    except Exception:
        # manual replaces if latin1 fails
        t = text
        rep = {
            'Ã¡': 'á', 'Ã©': 'é', 'Ã­': 'í', 'Ã³': 'ó', 'Ãº': 'ú',
            'Ã‘': 'Ñ', 'Ã±': 'ñ', 'Â¡': '¡', 'Â¿': '¿', 'â€¦': '…',
            'â€œ': '"', 'â€': '"', 'â€™': "'", 'â€”': '—', 'â€“': '–',
            'ðŸŽ™': '📢', 'ðŸŽ­': '🎭', 'ðŸ ¼': '🍼', 'ðŸ‘„': '👄',
            'ðŸ º': '🐺', 'ðŸ§›': '🧛', 'ðŸŒ ': '🌏'
        }
        for k, v in rep.items():
            t = t.replace(k, v)
        return t

# Clean data/dramatube.json
with open('data/dramatube.json', 'r', encoding='utf-8') as f:
    dramas = json.load(f)

for d in dramas:
    d['title'] = fix_mojibake(d.get('title', ''))
    d['original_title'] = d['title']
    c_sh, _ = normalize_shelf(d.get('shelf', ''))
    d['shelf'] = c_sh
    d['shelves'] = [c_sh]
    for ep in d.get('episodes', {}).values():
        if 'title' in ep:
            ep['title'] = fix_mojibake(ep['title'])

with open('data/dramatube.json', 'w', encoding='utf-8') as f:
    json.dump(dramas, f, ensure_ascii=False, indent=2)

# Clean data/dramatube_shelves.json
shelves_order = [
    'Nuevos Lanzamientos',
    'CLASIFICACIÓN',
    'Serie Doblada 📢',
    'Identidad Oculta 🎭',
    'Relación Tabú',
    'Bebés y Embarazos 🍼',
    'Amor a Primera Vista 👄',
    'Género Masculino',
    'Hombre Lobo 🐺 y Vampiro 🧛',
    'Historias de Asia 🌏',
    'Más Recomendados'
]

grouped = {sh: [] for sh in shelves_order}
for d in dramas:
    sh = d.get('shelf')
    if sh in grouped:
        grouped[sh].append(d)
    else:
        grouped.setdefault('Más Recomendados', []).append(d)

shelves_data = []
for sh in shelves_order:
    items = grouped[sh]
    _, icon = normalize_shelf(sh)
    slug = re.sub(r'[^a-z0-9]+', '-', sh.lower()).strip('-')
    shelves_data.append({
        'name': sh,
        'icon': icon,
        'slug': slug,
        'count': len(items),
        'items': [{
            'slug': x['slug'],
            'title': x['title'],
            'poster': x['poster'],
            'total_episodes': x['total_episodes'],
            'shelf': sh
        } for x in items]
    })

with open('data/dramatube_shelves.json', 'w', encoding='utf-8') as f:
    json.dump({'shelves': shelves_data, 'total_dramas': len(dramas)}, f, ensure_ascii=False, indent=2)

print("Successfully cleaned and formatted data/dramatube.json and data/dramatube_shelves.json!")
for s in shelves_data:
    print(f"  {s['icon']} {s['name']}: {s['count']} dramas")
