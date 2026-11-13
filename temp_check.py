with open('Auto/autoos_interactive.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re

# Find USERS array
for m in re.finditer(r'USERS|usuarios|users_list', text, re.IGNORECASE):
    start = max(0, m.start() - 50)
    end = min(len(text), m.end() + 400)
    print(f'Match at {m.start()}:')
    print(text[start:end])
    print('---')
    break

# Find where currentUser is set from a list
for m in re.finditer(r'useState.*(?:carlos|laura|andres|admin|guest|mecanico|conductor|pasajero)', text, re.IGNORECASE):
    start = max(0, m.start() - 100)
    end = min(len(text), m.end() + 300)
    print(f'useState user at {m.start()}:')
    print(text[start:end])
    print('---')
    break
