#!/bin/bash
echo "Yant Installer Is Starting..."

HOME_DIR="$HOME"
YANT="$HOME_DIR/yant"
NANO_DIR="$HOME_DIR/.nano"
NANO_FILE="$NANO_DIR/yant.nanorc"
BASHRC="$HOME_DIR/.bashrc"

if ! command -v python3 >/dev/null 2>&1; then
    echo "Python Not Found Installing..."
    pkg install -y python
fi

echo "Yant script is creating..."
cat > "$YANT" <<'EOF'
#!/usr/bin/env python3
import sys, re
variables = {}
if len(sys.argv) != 2:
    print("usage: yant filename.y")
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
    let_match = re.match(r'^LET\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(.+)$', line)
    if let_match:
        var_name = let_match.group(1)
        expr = let_match.group(2)
        try:
            value = eval(expr, {}, variables)
            variables[var_name] = value
        except Exception as e:
            print(f"Error: Line {i} → LET error ({e})")
        continue
    print_match = re.match(r'^PRINT\s*\(\s*(.+)\s*\)\s*$', line)
    if print_match:
        expr = print_match.group(1)
        try:
            if expr.startswith('"') and expr.endswith('"'):
                print(expr[1:-1])
            else:
                result = eval(expr, {}, variables)
                print(result)
        except Exception as e:
            print(f"Error: Line {i} → PRINT error ({e})")
        continue
    print(f"Error: Line {i} Unknown Syntax -> {line}")
EOF

chmod +x "$YANT"
echo "Yant script is created."

mkdir -p "$NANO_DIR"
cat > "$NANO_FILE" <<'EOL'
syntax "yant" "\.y$"
color brightred "\bPRINT\b"
color brightblue "\([^)]+\)"
color green "\"[^\"]*\""
color yellow "\bLET\b"
color white "^#.*$"
EOL
echo "Nano syntax is created."

if ! grep -Fxq "include \"$NANO_FILE\"" "$HOME_DIR/.nanorc"; then
    echo "include \"$NANO_FILE\"" >> "$HOME_DIR/.nanorc"
fi
echo "Nano settings are made."

# 5. PATH
if [[ ":$PATH:" != *":$HOME_DIR:"* ]]; then
    echo "export PATH=\$PATH:$HOME_DIR" >> "$BASHRC"
fi
echo "PATH settings are made"

echo "Installer completed! You Can Test With 'yant test.y'"
