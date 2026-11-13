# -*- coding: utf-8 -*-
import re
import subprocess
import os

with open('Auto/autoos_interactive.html', 'r', encoding='utf-8') as f:
    text = f.read()

m = re.search(r'<script\s+type=[\"\']module[\"\']>(.*?)</script>', text, re.DOTALL)
if m:
    with open('scratch_check_script.js', 'w', encoding='utf-8') as out:
        out.write(m.group(1))
    print('Extracted script, size:', len(m.group(1)))
    res = subprocess.run(['node', '--check', 'scratch_check_script.js'], capture_output=True, text=True)
    print('node --check returncode:', res.returncode)
    if res.stdout:
        print('stdout:', res.stdout)
    if res.stderr:
        print('stderr:', res.stderr)
    if os.path.exists('scratch_check_script.js'):
        os.remove('scratch_check_script.js')
else:
    print('Script tag not found')
