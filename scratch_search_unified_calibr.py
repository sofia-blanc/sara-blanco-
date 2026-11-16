with open('Auto/autoos_unified.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
m = list(re.finditer(r'calibr|Simulador & Configurador', text, re.I))
print('Matches in autoos_unified.html:', len(m))
for item in m:
    idx = item.start()
    print('At', idx, ':', text[max(0, idx-40):idx+120])
    print('---')
