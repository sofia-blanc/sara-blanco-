with open('Auto/autoos_interactive.html', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('Simulador & Configurador Total de Fallas')
if idx == -1:
    idx = text.find('Simulador & Configurador')
if idx == -1:
    idx = text.find('Configurador')
print('Configurador at:', idx)
if idx != -1:
    print(text[max(0, idx-300):idx+800])
