# -*- coding: utf-8 -*-
import re
import subprocess
import os

with open('Auto/autoos_unified.html', 'r', encoding='utf-8') as f:
    text = f.read()

m = re.findall(r'<script\s+type=[\"\']module[\"\']>(.*?)</script>', text, re.DOTALL)
print(f'Found {len(m)} module scripts in unified.html')
for i, s in enumerate(m):
    fname = f'scratch_unified_check_{i}.js'
    with open(fname, 'w', encoding='utf-8') as out:
        out.write(s)
    res = subprocess.run(['node', '--check', fname], capture_output=True, text=True)
    print(f'Script {i} (size {len(s)}) returncode: {res.returncode}')
    if res.stderr:
        print(f'Script {i} stderr: {res.stderr}')
    if os.path.exists(fname):
        os.remove(fname)
