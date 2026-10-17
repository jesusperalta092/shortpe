import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('scratch/node6.js', 'r', encoding='utf-8') as f:
    js = f.read()

pos = js.find('const i=bi(t),a=Ci(r().slug)')
if pos != -1:
    print(js[pos-800:pos+300])
