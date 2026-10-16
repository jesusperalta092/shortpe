import json

hd = json.load(open('data/hotdrama.json', encoding='utf-8'))
by_slug = {d['slug']: d for d in hd}

shelves_def = [
    {
        'name': 'Top Tendencias',
        'icon': '🔥',
        'slugs': [
            'nt-aventura-prohibida-con-el-papa-de-mi-mejor-amiga-doblado',
            'nt-besando-al-hermano-equivocado',
            'nt-besare-tus-cicatrices',
            'nt-consentida-del-senor-ferrer',
            'nt-doblada-dos-suenos-un-despertar',
            'nt-doblada-la-duena-del-karma',
            'nt-ecos-de-la-fatalidad',
            'nt-el-cazador-legendario',
            'nt-el-despertar-del-dios-mortal-doblado',
            'nt-el-es-mas-apasionado-que-mi-ex',
            'nt-embarazada-de-trillizos-del-rey-dragon',
            'nt-esposa-del-magnate-oculto'
        ]
    },
    {
        'name': 'Romance CEO & Millonarios',
        'icon': '💍',
        'slugs': [
            'nt-aventura-prohibida-con-el-papa-de-mi-mejor-amiga-doblado',
            'nt-consentida-del-senor-ferrer',
            'nt-esposa-del-magnate-oculto',
            'nt-me-enamore-del-padre-millonario-de-mi-amiga',
            'nt-la-tierra-baldia-que-me-hizo-millonario-doblado',
            'nt-doblada-dos-suenos-un-despertar',
            'nt-el-ultimo-baile-por-amor',
            'nt-cautiva-en-la-jaula-de-oro',
            'nt-o-cesar-o-nada'
        ]
    },
    {
        'name': 'Hombres Lobo & Fantasía',
        'icon': '🐺',
        'slugs': [
            'nt-embarazada-de-trillizos-del-rey-dragon',
            'nt-rechazame-rey-dragon',
            'nt-el-lobo-que-vive-conmigo',
            'nt-el-cazador-legendario',
            'nt-el-despertar-del-dios-mortal-doblado',
            'nt-tu-pequena-dulzura-es-la-heredera-de-hades',
            'nt-un-pacto-me-unio-al-inmortal-supremo-1',
            'nt-la-centesima-traicion'
        ]
    },
    {
        'name': 'Amor Prohibido & Pasión',
        'icon': '💋',
        'slugs': [
            'nt-aventura-prohibida-con-el-papa-de-mi-mejor-amiga-doblado',
            'nt-el-es-mas-apasionado-que-mi-ex',
            'nt-mi-hermanastro-es-un-bad-boy',
            'nt-rendida-a-su-oscuro-secreto',
            'nt-angel-y-la-bestia',
            'nt-besando-al-hermano-equivocado',
            'nt-besare-tus-cicatrices',
            'nt-cautiva-en-la-jaula-de-oro'
        ]
    },
    {
        'name': 'Venganza & Segundas Oportunidades',
        'icon': '👑',
        'slugs': [
            'nt-doblada-la-duena-del-karma',
            'nt-ecos-de-la-fatalidad',
            'nt-mi-angel-de-la-fortuna-me-hizo-reina-doblado',
            'nt-mi-barco-del-amor-zarpo-sin-ti',
            'nt-la-abogada-del-baile-enmascarado',
            'nt-playboy-el-verdadero-dios',
            'nt-entre-la-niebla-y-el-viento',
            'nt-el-medico-divino-rodeado-de-siete-bellezas-2',
            'nt-la-centesima-traicion'
        ]
    },
    {
        'name': 'Doblaje Latino Completo',
        'icon': '🎙️',
        'slugs': [d['slug'] for d in hd]
    }
]

out_shelves = []
for s in shelves_def:
    items = []
    for sl in s['slugs']:
        if sl in by_slug:
            it = dict(by_slug[sl])
            it.pop('episodes', None)
            items.append(it)
    out_shelves.append({
        'name': s['name'],
        'icon': s['icon'],
        'count': len(items),
        'items': items[:10],
        'all_items': items
    })

data = {'shelves': out_shelves}
with open('data/hotdrama_shelves.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Generado data/hotdrama_shelves.json con {len(out_shelves)} categorías temáticas.")
for s in out_shelves:
    print(f" - {s['icon']} {s['name']}: {s['count']} títulos")
