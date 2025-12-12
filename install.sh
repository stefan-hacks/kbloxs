#!/bin/bash
# Installation script for blocks_kitten

set -e

KITTY_CONFIG_DIR="${HOME}/.config/kitty"
KITTENS_DIR="${KITTY_CONFIG_DIR}/kittens"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="${HOME}/.local/bin"

echo "Installing blocks_kitten for Kitty terminal..."
echo ""

# Create directories if they don't exist
mkdir -p "${KITTENS_DIR}"
mkdir -p "${BIN_DIR}"
mkdir -p "${KITTY_CONFIG_DIR}"

# Copy blocks_kitten to kittens directory
if [ -d "${SCRIPT_DIR}/blocks_kitten" ]; then
    # Remove old installation if exists
    if [ -d "${KITTENS_DIR}/blocks_kitten" ]; then
        rm -rf "${KITTENS_DIR}/blocks_kitten"
    fi
    cp -r "${SCRIPT_DIR}/blocks_kitten" "${KITTENS_DIR}/"
    echo "✓ Installed blocks_kitten kitten"
else
    echo "Error: blocks_kitten directory not found in ${SCRIPT_DIR}"
    exit 1
fi

# Make ALL Python files executable
find "${KITTENS_DIR}/blocks_kitten" -name "*.py" -type f -exec chmod +x {} \;
echo "✓ Made all Python files executable"

# Verify __init__.py exports main correctly
if ! grep -q "from .main import main" "${KITTENS_DIR}/blocks_kitten/__init__.py" 2>/dev/null; then
    cat > "${KITTENS_DIR}/blocks_kitten/__init__.py" << 'EOF'
# Kitty kitten for block and tabular output
from .main import main
__all__ = ['main']
EOF
    echo "✓ Fixed __init__.py"
fi

# Verify structured_data.py exists (required for advanced features)
if [ ! -f "${KITTENS_DIR}/blocks_kitten/structured_data.py" ]; then
    echo "Warning: structured_data.py not found - advanced features may not work"
fi

# Install blx command
if [ -f "${SCRIPT_DIR}/blx" ]; then
    cp -f "${SCRIPT_DIR}/blx" "${BIN_DIR}/"
    chmod +x "${BIN_DIR}/blx"
    echo "✓ Installed 'blx' command to ${BIN_DIR}/blx"
else
    echo "Warning: blx script not found"
fi

# Ensure ~/.local/bin is in PATH
SHELL_CONFIG=""
if [ -f "${HOME}/.bashrc" ]; then
    SHELL_CONFIG="${HOME}/.bashrc"
elif [ -f "${HOME}/.zshrc" ]; then
    SHELL_CONFIG="${HOME}/.zshrc"
elif [ -f "${HOME}/.profile" ]; then
    SHELL_CONFIG="${HOME}/.profile"
fi

if [ -n "${SHELL_CONFIG}" ]; then
    PATH_EXPORT="export PATH=\"\${HOME}/.local/bin:\$PATH\""
    if ! grep -q "\.local/bin" "${SHELL_CONFIG}" 2>/dev/null; then
        echo "" >> "${SHELL_CONFIG}"
        echo "# Add local bin to PATH (for blx command)" >> "${SHELL_CONFIG}"
        echo "${PATH_EXPORT}" >> "${SHELL_CONFIG}"
        echo "✓ Added ${BIN_DIR} to PATH in ${SHELL_CONFIG}"
    else
        echo "✓ ${BIN_DIR} already in PATH configuration"
    fi
fi

# Add alias to shell configuration
ALIAS_LINE="alias b='blx'"
BASHRC="${HOME}/.bashrc"
BASH_ALIASES="${HOME}/.bash_aliases"
ZSHRC="${HOME}/.zshrc"

# Determine which config file to use
CONFIG_FILE=""
if [ -f "${BASH_ALIASES}" ]; then
    CONFIG_FILE="${BASH_ALIASES}"
elif [ -f "${BASHRC}" ]; then
    CONFIG_FILE="${BASHRC}"
elif [ -f "${ZSHRC}" ]; then
    CONFIG_FILE="${ZSHRC}"
fi

if [ -n "${CONFIG_FILE}" ]; then
    # Check if alias already exists (with or without quotes)
    if grep -qE "^alias b=['\"]?blx['\"]?" "${CONFIG_FILE}" 2>/dev/null; then
        echo "✓ Alias 'b' already exists in ${CONFIG_FILE}"
    else
        echo "" >> "${CONFIG_FILE}"
        echo "# Blocks kitten alias - use 'b <command>' instead of 'blx <command>'" >> "${CONFIG_FILE}"
        echo "${ALIAS_LINE}" >> "${CONFIG_FILE}"
        echo "✓ Added alias 'b' to ${CONFIG_FILE}"
    fi
else
    echo "Warning: Could not find shell configuration file (.bashrc, .bash_aliases, or .zshrc)"
    echo "  You may need to manually add: alias b='blx'"
fi

# Update kitty.conf with helpful comments
KITTY_CONF="${KITTY_CONFIG_DIR}/kitty.conf"

if [ ! -f "${KITTY_CONF}" ]; then
    # Create basic kitty.conf
    cat > "${KITTY_CONF}" << 'EOF'
# Kitty configuration file

# Blocks kitten - installed in ~/.config/kitty/kittens/blocks_kitten
# Use with: blx <command> or b <command>
# Example: blx ls -la
# Example: b ps aux --select USER,PID,COMMAND
EOF
    echo "✓ Created ${KITTY_CONF}"
else
    # Check if blocks_kitten is already mentioned in kitty.conf
    if ! grep -q "blocks_kitten\|Blocks kitten\|blx\|Blocks Kitten" "${KITTY_CONF}" 2>/dev/null; then
        echo "" >> "${KITTY_CONF}"
        echo "# Blocks kitten - installed in ~/.config/kitty/kittens/blocks_kitten" >> "${KITTY_CONF}"
        echo "# Use with: blx <command> or b <command>" >> "${KITTY_CONF}"
        echo "# Example: blx ls -la" >> "${KITTY_CONF}"
        echo "✓ Updated ${KITTY_CONF} with blocks_kitten information"
    else
        echo "✓ ${KITTY_CONF} already contains blocks_kitten information"
    fi
fi

# Verify installation
echo ""
echo "Verifying installation..."
VERIFY_FAILED=0

# Check if blx is accessible
if command -v blx >/dev/null 2>&1; then
    echo "✓ blx command is accessible"
elif [ -f "${BIN_DIR}/blx" ]; then
    # Test with full path
    if "${BIN_DIR}/blx" --help >/dev/null 2>&1; then
        echo "✓ blx command works (may need to reload shell for PATH)"
    else
        echo "✗ blx command found but not working"
        VERIFY_FAILED=1
    fi
else
    echo "✗ blx command not found"
    VERIFY_FAILED=1
fi

# Check if kitten files exist
if [ -f "${KITTENS_DIR}/blocks_kitten/main.py" ] && [ -f "${KITTENS_DIR}/blocks_kitten/__init__.py" ]; then
    echo "✓ Kitten files installed correctly"
    
    # Test Python import
    if python3 -c "import sys; sys.path.insert(0, '${KITTENS_DIR}'); import blocks_kitten; hasattr(blocks_kitten, 'main')" 2>/dev/null; then
        echo "✓ Kitten module can be imported"
    else
        echo "⚠ Kitten module import test failed (may still work)"
    fi
else
    echo "✗ Kitten files missing"
    VERIFY_FAILED=1
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ $VERIFY_FAILED -eq 0 ]; then
    echo "✓ Installation complete and verified!"
else
    echo "⚠ Installation complete but verification found issues"
fi
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Usage:"
echo "  blx <command> [args...]              # Long form"
echo "  b <command> [args...]                # Short alias"
echo ""
echo "Examples:"
echo "  blx ls -la"
echo "  blx ps aux"
echo "  blx ps aux --select USER,PID,COMMAND --limit 5"
echo "  b git status"
echo "  b docker ps"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "IMPORTANT - Next Steps:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. RELOAD YOUR SHELL (choose one):"
echo "   source ~/.bashrc"
echo "   # OR just open a new terminal"
echo ""
echo "2. TEST THE INSTALLATION:"
echo "   blx echo 'Hello, World!'"
echo "   # If blx works, test the alias:"
echo "   b echo 'Test alias'"
echo ""
if [ -n "$KITTY_PID" ] || [ -n "$KITTY_WINDOW_ID" ]; then
    echo "3. You're in Kitty terminal - restart Kitty for best results:"
    echo "   Close and reopen Kitty to refresh kitten registry"
else
    echo "3. For best experience, use Kitty terminal"
fi
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

