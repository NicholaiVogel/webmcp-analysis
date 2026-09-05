import json, re
index=json.load(open('analysis/fleet/index.json'))
for name in ['r2-0309','r2-0452','r2-0507','r2-0522']:
    prompt=open(f'analysis/fleet/prompts/{name}.txt').read()
    nprompt=prompt.count('PROJECT ')
    exp=len([e for e in index if e['reviewer']==name+'.txt'][0]['slugs'])
    print(f"{name}: prompt_packets={nprompt} index_expected={exp}")
