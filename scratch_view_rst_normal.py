with open('Auto/autoos_unified.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = list(re.finditer(r'Restablecer Sistema a Normal', text))
print('Count:', len(matches))
for m in matches:
    idx = m.start()
    print('At', idx)
    print(text[max(0, idx-50):idx+350])
    print('---')
