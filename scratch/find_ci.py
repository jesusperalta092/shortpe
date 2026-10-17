import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('scratch/node6.js', 'r', encoding='utf-8') as f:
    js = f.read()

idx = js.find('function Ci')
if idx != -1:
    print(js[idx-100:idx+400])
else:
    # search Ci=
    import re
    matches = re.findall(r'.{0,100}Ci\s*=\s*.{0,200}', js)
    for m in matches:
        print("Ci match:", m)
