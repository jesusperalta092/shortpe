import re
import json

with open('scratch/kurz_home_raw.html', 'r', encoding='utf-8') as f:
    home_html = f.read()

# Find the sveltekit script
m = re.search(r'__sveltekit_[a-zA-Z0-9]+\.resolve\([^,]+,\s*\(\)\s*=>\s*\(function\(([^)]*)\)\s*\{\s*return\s*(\[.*?\])\s*\}\((.*?)\)\)', home_html, re.DOTALL)
if m:
    params = [p.strip() for p in m.group(1).split(',')]
    ret_raw = m.group(2)
    args_raw = m.group(3)
    print("Found sveltekit serialized bundle!")
    print(f"Params count: {len(params)}")
    print(f"Return array length approx: {len(ret_raw)}")
    print(f"Args string length approx: {len(args_raw)}")
    
    # Save the script content to scratch for deeper inspection
    with open('scratch/svelte_home.js', 'w', encoding='utf-8') as out_f:
        out_f.write(m.group(0))
else:
    print("Pattern 1 didn't match directly, searching all resolve calls:")
    calls = re.findall(r'__sveltekit_[a-zA-Z0-9]+\.resolve\([^\)]*\)', home_html)
    print("Calls found:", len(calls))

# Also search for text patterns like "Nuevos Lanzamientos", "CLASIFICACIÓN", "Serie Doblada", "Unida al Alfa"
print("\nSearching for section names from user's screenshots:")
for term in ["Nuevos Lanzamientos", "CLASIFICACIÓN", "Serie Doblada", "Identidad Oculta", "Relación Tabú", "Bebés y Embarazos", "Amor a Primera Vista", "Hombre Lobo"]:
    idx = home_html.find(term)
    print(f"'{term}': index = {idx}")
    if idx != -1:
        snippet = home_html[max(0, idx-100): min(len(home_html), idx+300)]
        print("   Context:", repr(snippet))
