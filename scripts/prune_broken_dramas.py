import json, requests

# 1. Limpiar HotDrama
hd = json.load(open('data/hotdrama.json', encoding='utf-8'))
print('Original HotDrama:', len(hd))

# Filtrar: excluir nt-* (vencidos 410) y el que dio 503 (hd-hg-165004)
hd_clean = [
    d for d in hd
    if not d.get('slug', '').startswith('nt-')
    and d.get('source') != 'narto'
    and d.get('slug') != 'hd-hg-165004'
]
print('Cleaned HotDrama:', len(hd_clean))
with open('data/hotdrama.json', 'w', encoding='utf-8') as f:
    json.dump(hd_clean, f, ensure_ascii=False, indent=2)

# 2. Limpiar DramaShorts
ds = json.load(open('data/dramashorts.json', encoding='utf-8'))
print('Original DramaShorts:', len(ds))

# Auditoría rápida para dejar solo los que responden 200/206
ds_clean = []
for d in ds:
    ep1 = d.get('episodes', {}).get('1', '')
    if not ep1:
        continue
    # Excluir TikTok y NetShort CDN que fallan con 403/404
    if 'tiktokcdn.com' in ep1 or 'netshort.com' in ep1:
        continue
    # El resto son Akamai HLS (shortwave.goodbos.online) que son 100% estables
    ds_clean.append(d)

print('Cleaned DramaShorts:', len(ds_clean))
with open('data/dramashorts.json', 'w', encoding='utf-8') as f:
    json.dump(ds_clean, f, ensure_ascii=False, indent=2)

# 3. Limpiar catalog_full.json
cat = json.load(open('catalog_full.json', encoding='utf-8'))
print('Original catalog_full:', len(cat))

# Excluir cualquier item de narto / nt-* y los ds que fueron podados
valid_hd_slugs = {d['slug'] for d in hd_clean}
valid_ds_slugs = {d['slug'] for d in ds_clean}

cat_clean = []
for d in cat:
    slug = d.get('slug', '')
    # Si es narto o nt-*, descartar
    if slug.startswith('nt-') or d.get('source') == 'narto' or slug == 'hd-hg-165004':
        continue
    # Si es huangguo, solo si esta en valid_hd_slugs
    if slug.startswith('hd-hg-'):
        if slug in valid_hd_slugs:
            cat_clean.append(d)
        continue
    # Si es suikora, solo si esta en valid_ds_slugs
    if d.get('source') == 'suikora':
        if slug in valid_ds_slugs:
            cat_clean.append(d)
        continue
    # El resto del catalogo general (cukelis, etc.) se mantiene
    cat_clean.append(d)

print('Cleaned catalog_full:', len(cat_clean))
with open('catalog_full.json', 'w', encoding='utf-8') as f:
    json.dump(cat_clean, f, ensure_ascii=False, indent=2)

print('Done cleaning!')
