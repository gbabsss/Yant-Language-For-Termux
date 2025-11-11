#!/usr/bin/env python3
import os
import subprocess

home = os.environ['HOME']
yant_path = os.path.join(home, "yant")
nano_dir = os.path.join(home, ".nano")
nano_file = os.path.join(nano_dir, "yant.nanorc")
bashrc = os.path.join(home, ".bashrc")

print("Yant Installer Is Starting Up...")

try:
    subprocess.run(["python3", "--version"], check=True)
except subprocess.CalledProcessError:
    print("Python not found. Installing Python...")
    subprocess.run(["pkg", "install", "-y", "python"], check=True)

print("Yant Script Is Creating...")
yant_code = '''#!/usr/bin/env python3
import sys, re
variables = {}
if len(sys.argv) != 2:
    print("Usage: yant filename.y")
    sys.exit(1)
dosya = sys.argv[1]
try:
    with open(dosya, "r") as f:
        lines = f.readlines()
except FileNotFoundError:
    print(f"Error: {dosya} Is Not Found!")
    sys.exit(1)
for i, line in enumerate(lines, 1):
    line = line.strip()
    if line == "" or line.startswith("#"):
        continue
    let_match = re.match(r'^LET\\s+([a-zA-Z_][a-zA-Z0-9_]*)\\s*=\\s*(.+)$', line)
    if let_match:
        var_name = let_match.group(1)
        expr = let_match.group(2)
        try:
            value = eval(expr, {}, variables)
            variables[var_name] = value
        except Exception as e:
            print(f"Error: Line {i} → LET Error ({e})")
        continue
    print_match = re.match(r'^PRINT\\s*\\(\\s*(.+)\\s*\\)\\s*$', line)
    if print_match:
        expr = print_match.group(1)
        try:
            if expr.startswith('"') and expr.endswith('"'):
                print(expr[1:-1])
            else:
                result = eval(expr, {}, variables)
                print(result)
        except Exception as e:
            print(f"Error: Line {i} → PRINT Error ({e})")
        continue
    print(f"Error: Line {i} Syntax Not Found -> {line}")
'''
with open(yant_path, "w") as f:
    f.write(yant_code)
os.chmod(yant_path, 0o755)
print(f"Yant Is Ready To Use!")

print("Nano syntax is creating...")
os.makedirs(nano_dir, exist_ok=True)
with open(nano_file, "w") as f:
    f.write('''syntax "yant" "\\.y$"
color brightred "\\bPRINT\\b"
color brightblue "\\([^)]+\\)"
color green "\\"[^\\"]*\\"
color yellow "\\bLET\\b"
color white "^#.*$"
''')

nanorc_file = os.path.join(home, ".nanorc")
if os.path.exists(nanorc_file):
    with open(nanorc_file, "a+") as f:
        f.seek(0)
        if f'include "{nano_file}"' not in f.read():
            f.write(f'\ninclude "{nano_file}"\n')
else:
    with open(nanorc_file, "w") as f:
        f.write(f'include "{nano_file}"\n')
print("Nano is ready to use.")

path_line = f'export PATH=$PATH:{home}'
if path_line not in open(bashrc).read():
    with open(bashrc, "a") as f:
        f.write(f'\n{path_line}\n')
print("PATH is set up.")

print("Yant installer is completed you can test with 'yant test.y' ")
