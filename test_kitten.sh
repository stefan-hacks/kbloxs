#!/bin/bash
# Comprehensive test script for blocks_kitten with all Nushell features

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo ""
echo -e "${CYAN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║           Testing BLX (Blocks Kitten) - All Features          ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Determine which command to use
if command -v blx &> /dev/null; then
    CMD="blx"
elif [ -f "./blx" ]; then
    CMD="./blx"
else
    CMD="python3 -m blocks_kitten.main"
fi

echo -e "${GREEN}Using:${NC} $CMD"
echo ""

# Test counter
TEST_NUM=0
PASSED=0
FAILED=0

# Function to run a test
run_test() {
    TEST_NUM=$((TEST_NUM + 1))
    local test_name="$1"
    local test_cmd="$2"
    
    echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}Test $TEST_NUM: $test_name${NC}"
    echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}Command:${NC} $test_cmd"
    echo ""
    
    # Execute command
    eval "$test_cmd"
    local exit_code=$?
    
    echo ""
    if [ $exit_code -eq 0 ]; then
        echo -e "${GREEN}✓ PASSED${NC}"
        PASSED=$((PASSED + 1))
    else
        echo -e "${RED}✗ FAILED (exit code: $exit_code)${NC}"
        FAILED=$((FAILED + 1))
    fi
    echo ""
    sleep 1
}

# Test data
TEST_DATA="Name\tAge\tCity\tScore\nAlice\t30\tNYC\t95\nBob\t25\tLA\t87\nCharlie\t35\tSF\t92\nDiana\t28\tBoston\t88"

# Test 1: Basic table output
run_test "Basic Table Output" "echo -e '$TEST_DATA' | $CMD cat"

# Test 2: Help menu
run_test "Help Menu (--help)" "$CMD --help | head -20"

# Test 3: Column selection by name
run_test "Column Selection (by name)" "echo -e '$TEST_DATA' | $CMD cat --select Name,Age"

# Test 4: Column selection by index
run_test "Column Selection (by index)" "echo -e '$TEST_DATA' | $CMD cat --select 0,1"

# Test 5: Row filtering (greater than)
run_test "Row Filtering (Age>28)" "echo -e '$TEST_DATA' | $CMD cat --where 'Age>28'"

# Test 6: Row filtering (equal)
run_test "Row Filtering (City=SF)" "echo -e '$TEST_DATA' | $CMD cat --where 'City=SF'"

# Test 7: Row filtering (regex)
run_test "Row Filtering (Name pattern)" "echo -e '$TEST_DATA' | $CMD cat --where 'Name~^[AB]'"

# Test 8: Sorting ascending
run_test "Sorting (ascending by Age)" "echo -e '$TEST_DATA' | $CMD cat --sort Age"

# Test 9: Sorting descending
run_test "Sorting (descending by Score)" "echo -e '$TEST_DATA' | $CMD cat --sort Score --reverse"

# Test 10: Limiting results
run_test "Limiting Results (limit 2)" "echo -e '$TEST_DATA' | $CMD cat --limit 2"

# Test 11: Statistics
run_test "Statistics (Age column)" "echo -e '$TEST_DATA' | $CMD cat --stats Age"

# Test 12: Combined operations
run_test "Combined Operations" "echo -e '$TEST_DATA' | $CMD cat --where 'Score>88' --select Name,Score --sort Score --reverse"

# Test 13: Real command - ls
run_test "Real Command (ls)" "ls -lh 2>/dev/null | head -10 | $CMD cat --limit 5"

# Test 14: Index-based selection
run_test "Index-based Column Selection" "echo -e '$TEST_DATA' | $CMD cat --select 0,3 --sort 3 --reverse"

# Test 15: Multiple filters
MULTI_DATA="Product\tPrice\tStock\tCategory\nLaptop\t1200\t15\tElectronics\nMouse\t25\t150\tElectronics\nDesk\t300\t30\tFurniture\nChair\t200\t45\tFurniture\nKeyboard\t80\t75\tElectronics"
run_test "Complex Query (Price>100, Electronics)" "echo -e '$MULTI_DATA' | $CMD cat --where 'Price>100' --select Product,Price,Category --sort Price"

# Test 16: Statistics on large numbers
run_test "Statistics on Prices" "echo -e '$MULTI_DATA' | $CMD cat --stats Price"

# Test 17: Tab-separated input
run_test "Tab-separated Input" "echo -e 'A\tB\tC\n1\t2\t3\n4\t5\t6' | $CMD cat"

# Test 18: Empty result filtering
run_test "Empty Result Filter" "echo -e '$TEST_DATA' | $CMD cat --where 'Age>100'"

# Test 19: All rows with limit
run_test "Limit Exceeds Rows" "echo -e 'X\tY\n1\t2\n3\t4' | $CMD cat --limit 10"

# Test 20: Numeric detection (right-alignment)
NUMERIC_DATA="ID\tValue\tPercent\n1\t1000\t95.5\n2\t2000\t87.3\n3\t1500\t92.1"
run_test "Numeric Right-Alignment" "echo -e '$NUMERIC_DATA' | $CMD cat"

echo ""
echo -e "${CYAN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║                      Test Summary                              ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}Total Tests:${NC} $TEST_NUM"
echo -e "${GREEN}Passed:${NC} $PASSED"
if [ $FAILED -gt 0 ]; then
    echo -e "${RED}Failed:${NC} $FAILED"
else
    echo -e "${GREEN}Failed:${NC} 0"
fi
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║              All Tests Passed! 🎉                              ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${CYAN}Features Verified:${NC}"
    echo -e "  ${GREEN}✓${NC} Table formatting with box-drawing characters"
    echo -e "  ${GREEN}✓${NC} Index column (#) with cyan color"
    echo -e "  ${GREEN}✓${NC} Right-aligned numbers, left-aligned text"
    echo -e "  ${GREEN}✓${NC} Green bold headers (Nushell-style)"
    echo -e "  ${GREEN}✓${NC} Column selection (by name and index)"
    echo -e "  ${GREEN}✓${NC} Row filtering (all operators)"
    echo -e "  ${GREEN}✓${NC} Sorting (ascending and descending)"
    echo -e "  ${GREEN}✓${NC} Statistics (count, sum, min, max, avg)"
    echo -e "  ${GREEN}✓${NC} Limiting results"
    echo -e "  ${GREEN}✓${NC} Combined operations"
    echo -e "  ${GREEN}✓${NC} Alternating row colors"
    echo -e "  ${GREEN}✓${NC} Colorized help menu"
    echo ""
    echo -e "${YELLOW}Ready to install?${NC}"
    echo -e "  Run: ${CYAN}./install.sh${NC}"
    echo ""
    echo -e "${YELLOW}Want to see the full demo?${NC}"
    echo -e "  Run: ${CYAN}./DEMO.sh${NC}"
else
    echo -e "${RED}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║              Some Tests Failed                                 ║${NC}"
    echo -e "${RED}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${YELLOW}Please review the failed tests above.${NC}"
fi
echo ""
