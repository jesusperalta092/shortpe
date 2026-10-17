import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('scratch/node6.js', 'r', encoding='utf-8') as f:
    js = f.read()

idx = js.find('async function Ft')
if idx != -1:
    print(js[idx-500:idx+1500])
