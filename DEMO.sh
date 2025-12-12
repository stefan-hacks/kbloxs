#!/bin/bash
# Comprehensive demonstration of all Nushell-like features in blx

# Color codes for demo text
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo -e "${CYAN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║         BLX (Blocks Kitten) - Nushell Features Demo           ║${NC}"
echo -e "${CYAN}║              Beautiful Tables & Data Operations                ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Test data
TEST_DATA="Name\tAge\tCity\tSalary\nAlice\t30\tNYC\t75000\nBob\t25\tLA\t65000\nCharlie\t35\tSF\t85000\nDiana\t28\tBoston\t70000\nEve\t32\tSeattle\t80000"

echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}1. Basic Table with Index Column${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Command:${NC} echo -e 'Name\\tAge\\tCity\\tSalary\\n...' | ./blx cat"
echo ""
echo -e "$TEST_DATA" | ./blx cat
echo ""
echo -e "${CYAN}✓ Notice: Index column (#), right-aligned numbers, left-aligned text${NC}"
echo ""
read -p "Press Enter to continue..."
clear

echo ""
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}2. Column Selection by Name${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Command:${NC} ./blx cat --select Name,Age,Salary"
echo ""
echo -e "$TEST_DATA" | ./blx cat --select Name,Age,Salary
echo ""
echo -e "${CYAN}✓ Notice: Only selected columns displayed${NC}"
echo ""
read -p "Press Enter to continue..."
clear

echo ""
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}3. Column Selection by Index${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Command:${NC} ./blx cat --select 0,1,3"
echo -e "${BLUE}Info:${NC} 0=Name, 1=Age, 3=Salary (zero-based indexing)"
echo ""
echo -e "$TEST_DATA" | ./blx cat --select 0,1,3
echo ""
echo -e "${CYAN}✓ Notice: Same result as using column names${NC}"
echo ""
read -p "Press Enter to continue..."
clear

echo ""
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}4. Row Filtering - Greater Than${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Command:${NC} ./blx cat --where 'Age>28'"
echo ""
echo -e "$TEST_DATA" | ./blx cat --where "Age>28"
echo ""
echo -e "${CYAN}✓ Notice: Only rows where Age > 28${NC}"
echo ""
read -p "Press Enter to continue..."
clear

echo ""
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}5. Row Filtering - Exact Match${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Command:${NC} ./blx cat --where 'City=SF'"
echo ""
echo -e "$TEST_DATA" | ./blx cat --where "City=SF"
echo ""
echo -e "${CYAN}✓ Notice: Only rows where City equals SF${NC}"
echo ""
read -p "Press Enter to continue..."
clear

echo ""
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}6. Row Filtering - Pattern Match (Regex)${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Command:${NC} ./blx cat --where 'Name~^[AB]' (starts with A or B)"
echo ""
echo -e "$TEST_DATA" | ./blx cat --where "Name~^[AB]"
echo ""
echo -e "${CYAN}✓ Notice: Only rows where Name matches the regex pattern${NC}"
echo ""
read -p "Press Enter to continue..."
clear

echo ""
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}7. Sorting - Ascending${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Command:${NC} ./blx cat --sort Age"
echo ""
echo -e "$TEST_DATA" | ./blx cat --sort Age
echo ""
echo -e "${CYAN}✓ Notice: Sorted by Age (ascending: 25, 28, 30, 32, 35)${NC}"
echo ""
read -p "Press Enter to continue..."
clear

echo ""
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}8. Sorting - Descending${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Command:${NC} ./blx cat --sort Salary --reverse"
echo ""
echo -e "$TEST_DATA" | ./blx cat --sort Salary --reverse
echo ""
echo -e "${CYAN}✓ Notice: Sorted by Salary (descending: 85k, 80k, 75k, 70k, 65k)${NC}"
echo ""
read -p "Press Enter to continue..."
clear

echo ""
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}9. Limiting Results${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Command:${NC} ./blx cat --limit 3"
echo ""
echo -e "$TEST_DATA" | ./blx cat --limit 3
echo ""
echo -e "${CYAN}✓ Notice: Only first 3 rows displayed${NC}"
echo ""
read -p "Press Enter to continue..."
clear

echo ""
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}10. Statistics${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Command:${NC} ./blx cat --stats Age"
echo ""
echo -e "$TEST_DATA" | ./blx cat --stats Age
echo ""
echo -e "${CYAN}✓ Notice: Count, Sum, Min, Max, Avg calculated${NC}"
echo ""
read -p "Press Enter to continue..."
clear

echo ""
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}11. Combined Operations (Complex Query)${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Command:${NC} ./blx cat --where 'Salary>70000' --select Name,Age,Salary --sort Salary --reverse --limit 3"
echo -e "${BLUE}Query:${NC} Show top 3 earners making over 70k"
echo ""
echo -e "$TEST_DATA" | ./blx cat --where "Salary>70000" --select Name,Age,Salary --sort Salary --reverse --limit 3
echo ""
echo -e "${CYAN}✓ Notice: Multiple operations combined into one query${NC}"
echo ""
read -p "Press Enter to continue..."
clear

echo ""
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}12. Real-world Example - File Listing${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Command:${NC} ls -lh | ./blx cat --limit 10"
echo ""
ls -lh 2>/dev/null | head -15 | ./blx cat --limit 10
echo ""
echo -e "${CYAN}✓ Notice: Real command output formatted as table${NC}"
echo ""
read -p "Press Enter to continue..."
clear

echo ""
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}13. Colorized Help Menu${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Command:${NC} ./blx --help"
echo ""
./blx --help | head -40
echo ""
echo -e "${CYAN}✓ Notice: Beautiful colorized help with examples${NC}"
echo ""
read -p "Press Enter to finish..."
clear

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                    Demo Complete! 🎉                           ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${CYAN}Key Features Demonstrated:${NC}"
echo -e "  ${GREEN}✓${NC} Index column (#) with row numbers"
echo -e "  ${GREEN}✓${NC} Right-aligned numbers, left-aligned text"
echo -e "  ${GREEN}✓${NC} Green bold headers (Nushell-style)"
echo -e "  ${GREEN}✓${NC} Cyan index column"
echo -e "  ${GREEN}✓${NC} Perfect box-drawing borders"
echo -e "  ${GREEN}✓${NC} Column selection (by name or index)"
echo -e "  ${GREEN}✓${NC} Row filtering (=, !=, >, <, >=, <=, ~)"
echo -e "  ${GREEN}✓${NC} Sorting (ascending/descending)"
echo -e "  ${GREEN}✓${NC} Statistics (count, sum, min, max, avg)"
echo -e "  ${GREEN}✓${NC} Limiting results"
echo -e "  ${GREEN}✓${NC} Combined operations"
echo -e "  ${GREEN}✓${NC} Alternating row colors"
echo ""
echo -e "${YELLOW}Ready to install?${NC}"
echo -e "  Run: ${CYAN}./install.sh${NC}"
echo ""
echo -e "${YELLOW}Or test more:${NC}"
echo -e "  Run: ${CYAN}./test_kitten.sh${NC}"
echo ""
