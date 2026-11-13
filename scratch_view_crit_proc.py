with open('web/src/components/CriticalProcessSimulator.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

import re
m = list(re.finditer(r'canModify|userRole|calibr|onReset|Restablecer', text, re.I))
print('Matches in CriticalProcessSimulator:', len(m))
for item in m:
    idx = item.start()
    print('At', idx, ':', text[max(0, idx-40):idx+120])
    print('---')
