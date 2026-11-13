with open('Auto/autoos_unified.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = list(re.finditer(r'function onResetDevice|onResetDevice:\s*function', text))
print('Matches in autoos_unified.html:', len(matches))
for m in matches:
    idx = m.start()
    print('At', idx, ':', text[max(0, idx-50):idx+300])
