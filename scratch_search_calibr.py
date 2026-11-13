with open('Auto/autoos_interactive.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = list(re.finditer(r'calibr|Simulador & Configurador|Fallas Vehiculares', text, re.I))
for m in matches:
    idx = m.start()
    print('Match:', m.group(), 'at', idx)
    print(text[max(0, idx-50):idx+200])
    print('==============================')
