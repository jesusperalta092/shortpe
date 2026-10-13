import json, os, glob

print("--- Removiendo HuangguoDrama de HotDrama y Catalog ---")

# 1. Limpiar hotdrama.json
hd = json.load(open('data/hotdrama.json', encoding='utf-8'))
hd_clean = [d for d in hd if not (d.get('slug', '').startswith('hd-hg-') or d.get('source') == 'huangguo')]
print(f"data/hotdrama.json: de {len(hd)} a {len(hd_clean)}")
with open('data/hotdrama.json', 'w', encoding='utf-8') as f:
    json.dump(hd_clean, f, ensure_ascii=False, indent=2)

# 2. Limpiar catalog_full.json
cat = json.load(open('catalog_full.json', encoding='utf-8'))
cat_clean = [d for d in cat if not (d.get('slug', '').startswith('hd-hg-') or d.get('source') == 'huangguo')]
print(f"catalog_full.json: de {len(cat)} a {len(cat_clean)}")
with open('catalog_full.json', 'w', encoding='utf-8') as f:
    json.dump(cat_clean, f, ensure_ascii=False, indent=2)

# 3. Eliminar data/huangguo.json si existe
if os.path.exists('data/huangguo.json'):
    os.remove('data/huangguo.json')
    print("Eliminado data/huangguo.json")

# 4. Eliminar posters de Huangguo
posters_root = glob.glob('posters/hd-hg-*.jpg')
for p in posters_root:
    try: os.remove(p)
    except: pass
print(f"Eliminados {len(posters_root)} posters de posters/")

posters_web = glob.glob('web-next/public/posters/hd-hg-*.jpg')
for p in posters_web:
    try: os.remove(p)
    except: pass
print(f"Eliminados {len(posters_web)} posters de web-next/public/posters/")

print("--- Listo. HuangguoDrama completamente eliminado ---")
