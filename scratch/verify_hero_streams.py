import urllib.request, json

hot_slugs = [
    "nt-aventura-prohibida-con-el-papa-de-mi-mejor-amiga-doblado",
    "nt-besando-al-hermano-equivocado",
    "nt-besare-tus-cicatrices",
    "nt-consentida-del-senor-ferrer",
    "nt-doblada-dos-suenos-un-despertar",
    "nt-doblada-la-duena-del-karma",
    "nt-ecos-de-la-fatalidad",
    "nt-el-cazador-legendario",
    "nt-el-despertar-del-dios-mortal-doblado",
    "nt-el-es-mas-apasionado-que-mi-ex"
]

print("Verificando reproducción de los 10 títulos del Hero:")
for i, slug in enumerate(hot_slugs):
    try:
        # Check Next.js page
        r_page = urllib.request.urlopen(f"http://localhost:3000/ver/{slug}/1", timeout=10)
        # Check stream API
        r_stream = urllib.request.urlopen(f"http://127.0.0.1:8090/proxy/episode?slug={slug}&ep=1", timeout=10)
        st_data = json.loads(r_stream.read())
        print(f"#{i+1} {slug[:30]}... -> Page: {r_page.status} | Stream: {st_data.get('type')} ({st_data.get('player_type')}) OK")
    except Exception as e:
        print(f"#{i+1} {slug[:30]}... -> ERROR: {e}")
