#!/bin/bash
# Demonstration of all Nushell-like features in blx

echo "========================================="
echo "BLX (Blocks Kitten) - Nushell Features Demo"
echo "========================================="
echo ""

echo "1. Basic table with index column and colors"
echo "Command: echo -e 'Name\tAge\tCity\nAlice\t30\tNYC\nBob\t25\tLA\nCharlie\t35\tSF' | ./blx cat"
echo ""
echo -e "Name\tAge\tCity\nAlice\t30\tNYC\nBob\t25\tLA\nCharlie\t35\tSF" | ./blx cat
echo ""
echo "Press Enter to continue..."
read

echo "2. Column selection (by name)"
echo "Command: echo -e 'Name\tAge\tCity\nAlice\t30\tNYC\nBob\t25\tLA\nCharlie\t35\tSF' | ./blx cat --select Name,Age"
echo ""
echo -e "Name\tAge\tCity\nAlice\t30\tNYC\nBob\t25\tLA\nCharlie\t35\tSF" | ./blx cat --select Name,Age
echo ""
echo "Press Enter to continue..."
read

echo "3. Column selection (by index)"
echo "Command: echo -e 'Name\tAge\tCity\nAlice\t30\tNYC\nBob\t25\tLA\nCharlie\t35\tSF' | ./blx cat --select 0,1"
echo ""
echo -e "Name\tAge\tCity\nAlice\t30\tNYC\nBob\t25\tLA\nCharlie\t35\tSF" | ./blx cat --select 0,1
echo ""
echo "Press Enter to continue..."
read

echo "4. Row filtering"
echo "Command: echo -e 'Name\tAge\tCity\nAlice\t30\tNYC\nBob\t25\tLA\nCharlie\t35\tSF' | ./blx cat --where 'Age>27'"
echo ""
echo -e "Name\tAge\tCity\nAlice\t30\tNYC\nBob\t25\tLA\nCharlie\t35\tSF" | ./blx cat --where "Age>27"
echo ""
echo "Press Enter to continue..."
read

echo "5. Sorting"
echo "Command: echo -e 'Name\tAge\tCity\nAlice\t30\tNYC\nBob\t25\tLA\nCharlie\t35\tSF' | ./blx cat --sort Age --reverse"
echo ""
echo -e "Name\tAge\tCity\nAlice\t30\tNYC\nBob\t25\tLA\nCharlie\t35\tSF" | ./blx cat --sort Age --reverse
echo ""
echo "Press Enter to continue..."
read

echo "6. Statistics"
echo "Command: echo -e 'Name\tAge\tCity\nAlice\t30\tNYC\nBob\t25\tLA\nCharlie\t35\tSF' | ./blx cat --stats Age"
echo ""
echo -e "Name\tAge\tCity\nAlice\t30\tNYC\nBob\t25\tLA\nCharlie\t35\tSF" | ./blx cat --stats Age
echo ""
echo "Press Enter to continue..."
read

echo "7. Combined operations"
echo "Command: echo -e 'Name\tAge\tCity\nAlice\t30\tNYC\nBob\t25\tLA\nCharlie\t35\tSF\nDiana\t28\tBoston' | ./blx cat --where 'Age>26' --select Name,Age --sort Age --reverse"
echo ""
echo -e "Name\tAge\tCity\nAlice\t30\tNYC\nBob\t25\tLA\nCharlie\t35\tSF\nDiana\t28\tBoston" | ./blx cat --where "Age>26" --select Name,Age --sort Age --reverse
echo ""
echo "Press Enter to continue..."
read

echo "8. Colorized help menu"
echo "Command: ./blx --help"
echo ""
./blx --help
echo ""

echo "========================================="
echo "Demo complete! All Nushell features working!"
echo "========================================="

