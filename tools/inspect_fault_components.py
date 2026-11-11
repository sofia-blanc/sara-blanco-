with open('Auto/autoos_unified.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
print("Matriz de Salud matches:")
for m in re.finditer(r'Matriz de Salud', text):
    print(m.start(), text[m.start()-50:m.start()+150])

print("\nSimulador & Configurador matches:")
for m in re.finditer(r'Simulador & Configurador|Configurador Total', text):
    print(m.start(), text[m.start()-50:m.start()+150])
