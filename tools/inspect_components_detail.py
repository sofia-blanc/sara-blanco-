import sys

with open('Auto/autoos_unified.html', 'r', encoding='utf-8') as f:
    text = f.read()

def search_backward_function(pos):
    idx = text.rfind('function ', 0, pos)
    return text[idx:idx+80]

print("Health matrix function:", search_backward_function(1382670))
print("Fault simulator function:", search_backward_function(1443894))

# Let's find where they are rendered in JSX
import re
print("\nWhere is the health matrix component called?")
for m in re.finditer(r'children:\s*\(0,\s*E\.jsxDEV\)\((lt|ot|st|at|rt|ct|pt|dt|ft|gt|ht|wt|yt|kt|_t|bt|et|nt|vt)', text):
    call_str = text[m.start():m.start()+120]
    # check if relevant
    # let's list all function names defined in the custom components section
