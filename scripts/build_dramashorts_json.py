import json
import re

with open('scratch_suikora.html', 'r', encoding='utf-8') as f:
    text = f.read()

urls = re.findall(r'https?://[^\s"\'<>]+\.m3u8[^\s"\'<>]*', text)
clean_urls = [u.rstrip('\\').rstrip('"').rstrip("'") for u in urls]

episodes = {str(i): u for i, u in enumerate(clean_urls, 1)}

drama = {
    "slug": "mi-presa-facil-resulto-ser-el-rey-del-colegio",
    "title": "Mi presa fácil resultó ser el rey del colegio",
    "poster": "/posters/mi-presa-facil-resulto-ser-el-rey-del-colegio.webp",
    "description": "Luciana ingresa a una escuela peligrosa y necesita protección. Para evitar ser víctima de acoso, decide acercarse a Ángel, a quien cree débil y dócil. Sin embargo, descubre que él es en realidad el temido rey del colegio.",
    "section": "dramashorts",
    "source": "suikora",
    "genres": ["Drama", "Romance", "Escolar", "DramaShorts"],
    "total_episodes": len(episodes),
    "episodes": episodes
}

with open('data/dramashorts.json', 'w', encoding='utf-8') as f:
    json.dump([drama], f, ensure_ascii=False, indent=2)

print(f"Saved drama with {len(episodes)} episodes to data/dramashorts.json!")
