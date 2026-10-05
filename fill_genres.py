# -*- coding: utf-8 -*-
"""Clasifica los dramas por genero basandose en palabras clave del titulo/descripcion"""
import json, os, re

ROOT=r'C:\Users\USER\Downloads\Proyecto_Netflix_Dramas'
CAT=os.path.join(ROOT,'catalog_full.json')

# reglas: (keyword en texto lower, genero)
RULES=[
  (r'\b(alfa|alpha|lobo|werewolf|manada|lic[aá]n)\b','Werewolf'),
  (r'\b(vampir|sangre|blood|dracula)\b','Vampiro'),
  (r'\b(drag[oó]n|dragon|dragoness)\b','Dragón'),
  (r'\b(mafia|mafios|c[aá]rtel|cartel|capo|g[aá]ngster)\b','Mafia'),
  (r'\b(ceo|millonari|billonari|magnate|empresari|heredero|imperio|multimillonari)\b','Billonario'),
  (r'\b(magia|m[aá]gic|hechicer|bruja|hechizo|diosa|deidad|fantas[ií]a|inmortal|d[ií]oses)\b','Fantasía'),
  (r'\b(renacer|renac|reencarn|reborn|segunda vida|volv[ií])\b','Renacimiento'),
  (r'\b(venganz|venganza|revancha|rechaz|traicion)\b','Venganza'),
  (r'\b(amor|romance|enamor|boda|casamiento|matrimonio|esposa|esposo|novia|novio|coraz[oó]n|beso|pasi[oó]n|sedu[cs])\b','Romance'),
  (r'\b(militar|soldado|coronel|general|navy|capit[aá]n|guerra|polic[ií]a|oficial)\b','Militar'),
  (r'\b(doctor|doctora|m[eé]dic|hospital|cirujan)\b','Médico'),
  (r'\b(reina|rey|princesa|principe|pr[ií]ncipe|emperador|imperio|trono|corona|nobleza|duque|duquesa|conde|condesa)\b','Realeza'),
  (r'\b(secreto|misterio|misterios|oculto|enmascarad|m[aá]scara|identidad)\b','Misterio'),
  (r'\b(sistema|apocalipsis|apocal[ií]ptic|zombi|superviviente|resurrecci[oó]n|reino)\b','Sistema/Apocalipsis'),
  (r'\b(gatita|gato|zorro|tigre|loba|serpiente|dragona|f[eé]nix)\b','Criaturas'),
  (r'\b(ni[nñ]era|beb[eé]|hijo|hija|madre|padre|familia|hermano|hermana|gemelos|embaraz)\b','Familia'),
  (r'\b(amnesia|doble vida|equivocad|confusi[oó]n|mentira|mentir)\b','Drama'),
]
RULES=[(re.compile(k,re.I),v) for k,v in RULES]

def classify(title, desc):
    txt=(title+' '+desc).lower()
    genres=[]
    for rx,g in RULES:
        if rx.search(txt) and g not in genres:
            genres.append(g)
    if not genres: genres=['Drama']
    if 'Romance' not in genres and any(k in txt for k in ['amor','coraz','beso','pasi']):
        genres.insert(0,'Romance')
    # limitar a 3
    return genres[:3]

if __name__=='__main__':
    cat=json.load(open(CAT,encoding='utf-8'))
    print(f'Procesando {len(cat)} dramas...')
    counts={}
    for d in cat:
        d['genres']=classify(d.get('title',''), d.get('description',''))
        for g in d['genres']: counts[g]=counts.get(g,0)+1
    json.dump(cat, open(CAT,'w',encoding='utf-8'), indent=2, ensure_ascii=False)
    print('Generos asignados:')
    for g,c in sorted(counts.items(),key=lambda x:-x[1]):
        print(f'  {g:22s} {c}')
    print(f'\n[OK] Catalogo actualizado.')
