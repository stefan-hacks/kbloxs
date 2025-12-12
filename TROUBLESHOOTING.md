# Troubleshooting Guide

## "No kitten named blocks_kitten"

If you get this error even after installation:

### Solution 1: Use `blx` command instead

The `blx` command works even if kitty can't find the kitten directly:

```bash
blx ls -la
blx ps aux
```

The `blx` wrapper script will:
- Try to use `kitty +kitten blocks_kitten` if in Kitty terminal
- Fall back to running Python directly if not in Kitty or kitten not found

### Solution 2: Verify Installation

Check if the kitten is installed:

```bash
ls -la ~/.config/kitty/kittens/blocks_kitten/
```

Should show:
- `__init__.py` (with `from .main import main`)
- `main.py` (executable)

### Solution 3: Fix __init__.py

If `__init__.py` is missing the import, fix it:

```bash
cat > ~/.config/kitty/kittens/blocks_kitten/__init__.py << 'EOF'
# Kitty kitten for block and tabular output
from .main import main
__all__ = ['main']
EOF
```

### Solution 4: Reinstall

Run the installer again:

```bash
cd /path/to/gbloxs
./install.sh
```

### Solution 5: Use Python Directly

As a fallback, you can always use Python directly:

```bash
python3 ~/.config/kitty/kittens/blocks_kitten/main.py ls -la
```

Or create an alias:

```bash
alias blx='python3 ~/.config/kitty/kittens/blocks_kitten/main.py'
```

## "blx: command not found"

Make sure `~/.local/bin` is in your PATH:

```bash
echo 'export PATH="${HOME}/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

## "b: command not found"

The `b` alias is added during installation. Reload your shell:

```bash
source ~/.bashrc
```

Or check if it exists:

```bash
grep "alias b=" ~/.bashrc ~/.bash_aliases
```

## Kitten works with Python but not with kitty

If `python3 blocks_kitten/main.py` works but `kitty +kitten blocks_kitten` doesn't:

1. **Restart Kitty terminal** - Kitty may need to reload kitten registry
2. **Check kitty version** - Custom kittens require kitty 0.13.0+
   ```bash
   kitty --version
   ```
3. **Use `blx` instead** - The wrapper handles both cases automatically

## Testing

Test the installation:

```bash
# Test blx command
blx echo "Hello, World!"

# Test Python directly
python3 ~/.config/kitty/kittens/blocks_kitten/main.py echo "Test"

# Test import
python3 -c "import sys; sys.path.insert(0, '~/.config/kitty/kittens'); import blocks_kitten; print('OK')"
```

