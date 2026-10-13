import json, re, sys

sys.stdout.reconfigure(encoding='utf-8')

# Palabras y patrones característicos en español
SPANISH_KEYWORDS = [
    'el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas',
    'de', 'del', 'al', 'en', 'con', 'por', 'para', 'sin', 'sobre', 'entre',
    'mi', 'tu', 'su', 'mis', 'tus', 'sus', 'nuestro', 'nuestra',
    'amor', 'amante', 'amiga', 'amigo', 'esposo', 'esposa', 'marido', 'mujer',
    'padre', 'madre', 'papá', 'mamá', 'hijo', 'hija', 'hermano', 'hermana', 'hermanastro',
    'doblado', 'doblada', 'doblad', 'espanol', 'español', 'latino',
    'rey', 'reina', 'dragón', 'dios', 'mortal', 'supremo', 'inmortal',
    'secreto', 'verdad', 'traición', 'venganza', 'promesa', 'destino', 'fatalidad',
    'sueño', 'sueños', 'despertar', 'volver', 'renacer', 'cielo', 'niebla', 'viento',
    'corazón', 'alma', 'vida', 'muerte', 'boda', 'matrimonio', 'divorcio',
    'millonario', 'millonaria', 'magnate', 'jefe', 'patrón', 'señor', 'señora',
    'cautiva', 'jaula', 'oro', 'corona', 'cenizas', 'cicatrices', 'beso', 'besar',
    'besando', 'besaré', 'dueña', 'dueño', 'tierra', 'baile', 'abogada', 'médico',
    'embarazada', 'trillizos', 'pequeña', 'dulzura', 'heredera', 'lobo', 'ángel',
    'pacto', 'barco', 'zarpó', 'recházame', 'rendida', 'apasionado', 'césar',
    'consentida', 'cazador', 'legendario', 'verdadero', 'falsedad', 'mentira', 'castigo'
]

# Palabras alemanas e inglesas evidentes
NON_SPANISH_KEYWORDS = [
    'der', 'die', 'das', 'dem', 'den', 'des', 'ein', 'eine', 'einer', 'eines',
    'und', 'in', 'im', 'von', 'vom', 'mit', 'auf', 'aus', 'für', 'gegen',
    'mein', 'meine', 'meinem', 'meinen', 'meiner', 'ihr', 'ihre', 'ihrer',
    'kein', 'keine', 'nicht', 'nichts', 'nur', 'ohne', 'über',
    'liebe', 'milliardär', 'milliardärin', 'ehemann', 'ehefrau', 'kaiser', 'könig',
    'drillinge', 'verbrechen', 'schatz', 'siegel', 'schatten', 'krieger', 'erbin',
    'the', 'my', 'your', 'his', 'her', 'our', 'their', 'of', 'and', 'to', 'in',
    'love', 'bride', 'heir', 'ruler', 'realm', 'cheating', 'ex', 'queen', 'mother',
    'broke', 'heart', 'saved', 'him', 'kill', 'husband', 'billionaire'
]

hd = json.load(open('data/hotdrama.json', encoding='utf-8'))

spanish_list = []
non_spanish_list = []

for idx, item in enumerate(hd):
    title = item.get('title', '').strip()
    words = re.findall(r'[a-záéíóúüñ]+', title.lower())
    
    es_score = sum(1 for w in words if w in SPANISH_KEYWORDS)
    non_es_score = sum(1 for w in words if w in NON_SPANISH_KEYWORDS)
    
    # Signos o letras exclusivamente españolas
    has_spanish_chars = bool(re.search(r'[áéíóúñ¿¡]', title, re.IGNORECASE))
    
    # Marcadores directos
    is_dubbed = bool(re.search(r'doblado|doblada|español', title, re.IGNORECASE))
    
    print(f"[{idx+1:3d}] {title}")
    print(f"      ES Score: {es_score} | Non-ES Score: {non_es_score} | Special Chars: {has_spanish_chars} | Dubbed: {is_dubbed}")
    
    # Decisión
    if is_dubbed or (es_score > 0 and non_es_score == 0) or (has_spanish_chars and non_es_score == 0):
        spanish_list.append(item)
        print("      --> CLASSIFICATION: SPANISH")
    elif es_score > non_es_score and non_es_score <= 1:
        # e.g. "Mi hermanastro es un Bad Boy" -> Mi hermanastro es un (ES) + Bad Boy (borrowed slang)
        spanish_list.append(item)
        print("      --> CLASSIFICATION: SPANISH (Slang/Mixed)")
    else:
        non_spanish_list.append(item)
        print("      --> CLASSIFICATION: NON-SPANISH")

print("\n" + "="*50)
print(f"TOTAL SPANISH: {len(spanish_list)}")
print(f"TOTAL NON-SPANISH: {len(non_spanish_list)}")
