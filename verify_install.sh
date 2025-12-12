#!/bin/bash
# Verification script for blocks_kitten installation

echo "Verifying blocks_kitten installation..."
echo ""

ERRORS=0

# Check 1: blx command exists
echo -n "Checking blx command... "
if command -v blx >/dev/null 2>&1; then
    echo "✓ Found"
else
    if [ -f "${HOME}/.local/bin/blx" ]; then
        echo "⚠ Found but not in PATH (may need: source ~/.bashrc)"
    else
        echo "✗ Not found"
        ERRORS=$((ERRORS + 1))
    fi
fi

# Check 2: blx command works
echo -n "Testing blx command... "
if blx --help >/dev/null 2>&1; then
    echo "✓ Works"
else
    echo "✗ Failed"
    ERRORS=$((ERRORS + 1))
fi

# Check 3: Alias b exists
echo -n "Checking alias 'b'... "
if type b >/dev/null 2>&1; then
    echo "✓ Found (may need: source ~/.bashrc)"
else
    echo "⚠ Not loaded (add to shell config or run: source ~/.bashrc)"
fi

# Check 4: Kitten files exist
echo -n "Checking kitten files... "
KITTEN_DIR="${HOME}/.config/kitty/kittens/blocks_kitten"
if [ -f "${KITTEN_DIR}/main.py" ] && [ -f "${KITTEN_DIR}/__init__.py" ]; then
    echo "✓ Found"
else
    echo "✗ Missing"
    ERRORS=$((ERRORS + 1))
fi

# Check 5: Python files are executable
echo -n "Checking Python files are executable... "
if [ -x "${KITTEN_DIR}/main.py" ]; then
    echo "✓ Yes"
else
    echo "✗ No"
    ERRORS=$((ERRORS + 1))
fi

# Check 6: Module import
echo -n "Testing Python module import... "
if python3 -c "import sys; sys.path.insert(0, '${KITTEN_DIR}/..'); import blocks_kitten; hasattr(blocks_kitten, 'main')" 2>/dev/null; then
    echo "✓ Works"
else
    echo "⚠ Failed (may still work)"
fi

# Check 7: structured_data.py exists
echo -n "Checking structured_data.py... "
if [ -f "${KITTEN_DIR}/structured_data.py" ]; then
    echo "✓ Found"
else
    echo "⚠ Missing (advanced features won't work)"
fi

# Check 8: kitty.conf updated
echo -n "Checking kitty.conf... "
if grep -q "blocks_kitten\|blx\|Blocks kitten" "${HOME}/.config/kitty/kitty.conf" 2>/dev/null; then
    echo "✓ Contains blocks_kitten info"
else
    echo "⚠ No blocks_kitten info (not required)"
fi

echo ""
if [ $ERRORS -eq 0 ]; then
    echo "✓✓✓ Installation verified successfully! ✓✓✓"
    echo ""
    echo "Try it:"
    echo "  blx echo 'Hello, World!'"
    echo "  b ls -la"
    exit 0
else
    echo "✗✗✗ Found $ERRORS issue(s) - please run install.sh again ✗✗✗"
    exit 1
fi

