with open('web/src/components/CriticalProcessSimulator.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('Restablecer Todo a Nominal')
print('Restablecer Todo a Nominal at:', idx)
print(text[idx-200:idx+600])
