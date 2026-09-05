#!/bin/bash
# Fetch remaining Devpost pages one at a time via agent-browser (curl is 403-walled at volume)
cd /mnt/work/webmcp-analysis
python3 - <<'PYEOF'
import csv, os, subprocess
have = set(os.listdir('raw/pages'))
slugs = [r['slug'] for r in csv.DictReader(open('raw/all_projects.csv'))]
todo = [s for s in slugs if s + '.html' not in have]
print('todo:', len(todo), flush=True)
S = 'webmcp-scraper'
def run(*a, t=80):
    try:
        r = subprocess.run(['agent-browser', '--session', S] + list(a), capture_output=True, text=True, timeout=t)
        return (r.stdout or '') + (r.stderr or '')
    except subprocess.TimeoutExpired:
        return 'TIMEOUT'
for i, s in enumerate(todo, 1):
    run('open', f'https://devpost.com/software/{s}')
    run('wait', '1200', t=25)
    body = run('eval', "document.documentElement.outerHTML.length > 10000 ? document.documentElement.outerHTML : 'TOOSHORT'", t=30)
    html = body.strip().split('\n', 1)[-1] if 'TOOSHORT' not in body[:50] else ''
    if len(html) > 10000:
        with open(f'raw/pages/{s}.html', 'w') as f:
            f.write(html)
        st = 'ok'
    else:
        st = 'fail'
    if i % 25 == 0:
        print(f'{i}/{len(todo)} {st}', flush=True)
print('BROWSER FETCH DONE', flush=True)
PYEOF
