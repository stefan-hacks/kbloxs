#!/bin/bash
# Test script for blocks_kitten

echo "Testing blocks_kitten..."
echo ""

# Use blx if available, otherwise use python directly
if command -v blx &> /dev/null; then
    CMD="blx"
elif [ -f "./blx" ]; then
    CMD="./blx"
else
    CMD="python3 blocks_kitten/main.py"
fi

echo "Using: $CMD"
echo ""

# Test 1: Simple command
echo "Test 1: Simple echo command"
$CMD echo "Hello, World!"
echo ""
echo "---"
echo ""

# Test 2: ls command
echo "Test 2: ls -la (should detect table)"
$CMD ls -la | head -20
echo ""
echo "---"
echo ""

# Test 3: ps command
echo "Test 3: ps aux (should detect table)"
$CMD ps aux | head -15
echo ""
echo "---"
echo ""

# Test 4: df command
echo "Test 4: df -h (should detect table)"
$CMD df -h 2>/dev/null | head -15 || echo "df -h not available"
echo ""
echo "---"
echo ""

# Test 5: Command with error
echo "Test 5: Non-existent command (should show error)"
$CMD nonexistentcommand12345
echo ""
echo "---"
echo ""

echo "All tests completed!"
echo ""
echo "To use in your terminal:"
echo "  blx <command>    # Long form"
echo "  b <command>      # Short alias (after: source ~/.bashrc)"

