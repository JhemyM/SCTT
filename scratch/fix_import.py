import re

with open('SCTT.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add import audio at the top
if 'import audio\n' not in content:
    content = content.replace('import traceback\n', 'import traceback\nimport audio\n')
    # Or if traceback is not there:
    content = content.replace('import turtle\n', 'import turtle\nimport audio\n')

with open('SCTT.py', 'w', encoding='utf-8') as f:
    f.write(content)
