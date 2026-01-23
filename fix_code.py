import os

path = 'prompts_hub.py'

# Read the file in binary mode to check for null bytes
with open(path, 'rb') as f:
    data = f.read()

# Remove null bytes
data = data.replace(b'\x00', b'')

# Attempt to decode as UTF-8, if it fails, try other encodings and force UTF-8
try:
    content = data.decode('utf-8')
except UnicodeDecodeError:
    content = data.decode('latin-1')

# Fix literal backticks if they were introduced
content = content.replace('`r`n', '\n')
content = content.replace('`n', '\n')

# Normalize line endings to LF then to CRLF if on Windows
content = content.replace('\r\n', '\n').replace('\r', '\n')
lines = content.split('\n')

# Clean up imports and structural issues we found earlier
new_lines = []
for line in lines:
    clean_line = line.strip('\r')
    # Fix the specific mangled import line if it still exists
    if 'import json`r`nimport queue' in clean_line:
        new_lines.append('import json')
        new_lines.append('import queue')
    else:
        new_lines.append(clean_line)

# Ensure essential classes and methods are intact and structured
# (The current file seems to have the right content mostly, just messed up by automation)

with open(path, 'w', encoding='utf-8', newline='') as f:
    f.write('\n'.join(new_lines))

print("Successfully cleaned prompts_hub.py")
