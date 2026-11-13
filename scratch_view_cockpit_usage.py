with open('Auto/autoos_unified.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = list(re.finditer(r'__AUTOOS_COCKPIT_HTML__', text))
print('Count of __AUTOOS_COCKPIT_HTML__:', len(matches))
for m in matches:
    idx = m.start()
    print('At', idx, ':', text[max(0, idx-40):idx+120])
