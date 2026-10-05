import glob, json

terms = ['claimed by three alphas', 'claimed by 3 alphas', 'three alphas']
found_any = False
for fn in glob.glob('*.json') + glob.glob('data/*.json'):
    try:
        data = json.load(open(fn, encoding='utf-8'))
        items = []
        if isinstance(data, list): items = data
        elif isinstance(data, dict): items = data.values() if not 'items' in data else data['items']
        for it in items:
            if isinstance(it, dict):
                title = str(it.get('title', '')).lower()
                slug = str(it.get('slug', '')).lower()
                for t in terms:
                    if t in title or t in slug:
                        print(f"Found in {fn}: slug={it.get('slug')} | title={it.get('title')} | eps={it.get('total_episodes') or len(it.get('episodes') or {})}")
                        found_any = True
    except Exception:
        pass

if not found_any:
    print("Not found in local databases.")
