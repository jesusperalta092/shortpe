import json, sys

sys.stdout.reconfigure(encoding='utf-8')
from classify_hotdramas import spanish_list

print(f"Filtering HotDrama: Keeping {len(spanish_list)} Spanish dramas.")

# 1. Guardar data/hotdrama.json limpio
with open('data/hotdrama.json', 'w', encoding='utf-8') as f:
    json.dump(spanish_list, f, ensure_ascii=False, indent=2)
print("data/hotdrama.json actualizado exitosamente.")

# 2. Actualizar catalog_full.json
with open('catalog_full.json', 'r', encoding='utf-8') as f:
    cat = json.load(f)

# Mantener solo 'drama' (978 dramas en español) + los 31 hotdramas limpios en español
spanish_slugs = set(d['slug'] for d in spanish_list)

cleaned_cat = []
for d in cat:
    section = d.get('section', 'drama')
    if section == 'hotdrama':
        if d.get('slug') in spanish_slugs:
            cleaned_cat.append(d)
    elif section not in ('dramashorts', 'dramatube', 'serie', 'pelicula'):
        cleaned_cat.append(d)

print(f"catalog_full.json antes: {len(cat)} items -> ahora: {len(cleaned_cat)} items.")

with open('catalog_full.json', 'w', encoding='utf-8') as f:
    json.dump(cleaned_cat, f, ensure_ascii=False, indent=2)
print("catalog_full.json actualizado exitosamente.")
