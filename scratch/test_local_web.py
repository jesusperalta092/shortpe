import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

print("Fetching http://localhost:3000/seccion/dramatube ...")
try:
    r = requests.get('http://localhost:3000/seccion/dramatube', timeout=30)
    print("DramaTube page status:", r.status_code, "Length:", len(r.text))
    
    # Check for shelves in HTML
    shelves_to_check = [
        'Nuevos Lanzamientos',
        'CLASIFICACIÓN',
        'Serie Doblada',
        'Identidad Oculta',
        'Relación Tabú',
        'Bebés y Embarazos',
        'Amor a Primera Vista',
        'Género Masculino',
        'Hombre Lobo',
        'Historias de Asia',
        'Más Recomendados'
    ]
    for sh in shelves_to_check:
        found = sh in r.text
        print(f"  Shelf '{sh}' present: {found}")

    # Check for target drama
    target_found = 'Unida al Alfa y su Beta' in r.text
    print(f"Target drama 'Unida al Alfa y su Beta' present: {target_found}")

except Exception as e:
    print("Error fetching DramaTube page:", e)

print("\nFetching player page: http://localhost:3000/ver/dt-unida-al-alfa-y-su-beta-6a433648a0263ac457025610/1 ...")
try:
    r2 = requests.get('http://localhost:3000/ver/dt-unida-al-alfa-y-su-beta-6a433648a0263ac457025610/1', timeout=30)
    print("Player page status:", r2.status_code, "Length:", len(r2.text))
    print("Contains player title:", 'Unida al Alfa y su Beta' in r2.text)
except Exception as e:
    print("Error fetching Player page:", e)
