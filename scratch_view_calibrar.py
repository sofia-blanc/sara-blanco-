with open('Auto/autoos_interactive.html', 'r', encoding='utf-8') as f:
    text = f.read()

idx = 523071
print(text[idx-600:idx+400])
