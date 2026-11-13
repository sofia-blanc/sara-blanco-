with open('Auto/autoos_unified.html', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('Restablecer Todo a Nominal')
print('Restablecer Todo a Nominal at:', idx)
print(text[idx-200:idx+400])
