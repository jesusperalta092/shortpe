import urllib.request, json

# Test 1: shelves API
r1 = urllib.request.urlopen('http://127.0.0.1:8090/api/hotdrama/shelves')
d1 = json.loads(r1.read())
print('Hotdrama shelves count:', len(d1.get('shelves', [])))
for s in d1.get('shelves', []):
    print(f"  - {s['name']}: {s['count']} items")

# Test 2: DramaTube page
r2 = urllib.request.urlopen('http://localhost:3000/seccion/dramatube')
h2 = r2.read().decode('utf-8', errors='ignore')
print('\nDramaTube page status:', r2.status)
print('Badge present (should be False):', 'EXCLUSIVO EN DRAMATUBE' in h2)
print('Subtitle present (should be False):', 'Disfruta de las mejores series cortas' in h2)

# Test 3: HotDrama page
r3 = urllib.request.urlopen('http://localhost:3000/seccion/hotdrama')
h3 = r3.read().decode('utf-8', errors='ignore')
print('\nHotDrama page status:', r3.status)
print('HotDrama has Secciones toggle:', 'Secciones' in h3)
print('HotDrama has kurz-card:', 'kurz-card' in h3)

# Test 4: Dramas page
r4 = urllib.request.urlopen('http://localhost:3000/seccion/drama')
h4 = r4.read().decode('utf-8', errors='ignore')
print('\nDramas page status:', r4.status)
print('Dramas page has kurz-card:', 'kurz-card' in h4)
