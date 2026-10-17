import urllib.request, re

r = urllib.request.urlopen('http://localhost:3000/')
html = r.read().decode('utf-8', errors='ignore')

hero_titles = re.findall(r'class="hero-title">(.*?)</h1>', html)
print('Hero title in HTML:', hero_titles)

hot_titles = [
    "Aventura prohibida con el papá de mi mejor amiga (Doblado)",
    "Besando al hermano equivocado",
    "Besaré Tus Cicatrices",
    "Consentida del Señor Ferrer",
    "(DOBLADA)Dos Sueños, Un Despertar",
    "(DOBLADA)La Dueña del Karma",
    "Ecos de la Fatalidad",
    "El Cazador Legendario",
    "El despertar del Dios Mortal (Doblado)",
    "Él Es más Apasionado que mi Ex"
]

print("\nVerificando presencia en el bundle del Home:")
for t in hot_titles:
    found = (t in html) or (t.encode('ascii', 'xmlcharrefreplace').decode() in html)
    print(f" - {t[:35]}... -> {'OK' if found else 'NO ENCONTRADO'}")
