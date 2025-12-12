# Test Before Installing

## Quick Test

To verify all new features are working before installation:

### 1. Run the Comprehensive Demo
```bash
./DEMO.sh
```

This interactive demo shows:
- ✅ Basic table with index column (#)
- ✅ Column selection by name and index
- ✅ Row filtering (>, =, ~)
- ✅ Sorting (ascending/descending)
- ✅ Statistics (count, sum, min, max, avg)
- ✅ Combined operations
- ✅ Real-world examples
- ✅ Colorized help menu

**Press Enter after each demo to continue.**

---

### 2. Run the Automated Test Suite
```bash
./test_kitten.sh
```

This runs 20 automated tests covering:
- ✅ All table formatting features
- ✅ All data operations
- ✅ Edge cases
- ✅ Real command output
- ✅ Combined queries

**Results shown at the end with pass/fail summary.**

---

## Quick Manual Test

Test a simple command:

```bash
echo -e "Name\tAge\tCity\nAlice\t30\tNYC\nBob\t25\tLA\nCharlie\t35\tSF" | ./blx cat
```

Expected output:
```
╭───┬─────────┬─────┬──────╮
│ # │ Name    │ Age │ City │
├───┼─────────┼─────┼──────┤
│ 0 │ Alice   │  30 │ NYC  │
│ 1 │ Bob     │  25 │ LA   │
│ 2 │ Charlie │  35 │ SF   │
╰───┴─────────┴─────┴──────╯
```

---

## Test with Operations

### Column Selection
```bash
echo -e "Name\tAge\tCity\nAlice\t30\tNYC\nBob\t25\tLA\nCharlie\t35\tSF" | ./blx cat --select Name,Age
```

### Row Filtering
```bash
echo -e "Name\tAge\tCity\nAlice\t30\tNYC\nBob\t25\tLA\nCharlie\t35\tSF" | ./blx cat --where "Age>27"
```

### Sorting
```bash
echo -e "Name\tAge\tCity\nAlice\t30\tNYC\nBob\t25\tLA\nCharlie\t35\tSF" | ./blx cat --sort Age --reverse
```

### Combined
```bash
echo -e "Name\tAge\tCity\nAlice\t30\tNYC\nBob\t25\tLA\nCharlie\t35\tSF\nDiana\t28\tBoston" | ./blx cat --where "Age>27" --select Name,Age --sort Age --reverse
```

---

## What to Look For

### ✅ Perfect Formatting
- Box-drawing characters: `╭─┬─╮`, `├─┼─┤`, `╰─┴─╯`
- Index column (#) in cyan
- Green bold headers
- Right-aligned numbers (Age: `  30`, `  25`)
- Left-aligned text (Name: `Alice   `, `Bob     `)
- Clean borders with `│` separators

### ✅ Colors
- **Headers**: Green bold
- **Index (#)**: Cyan
- **Borders**: Gray/dim
- **Alternating rows**: Every other row slightly dimmed
- **Statistics**: Multi-colored (cyan, green, blue, magenta, yellow)

### ✅ Operations Working
- Column selection reduces columns
- Row filtering removes rows
- Sorting changes order
- Statistics show count, sum, min, max, avg
- Combined operations work together

---

## If Everything Looks Good

Install the tool:
```bash
./install.sh
```

Then use:
```bash
blx <command>    # Long form
b <command>      # Short alias (after: source ~/.bashrc)
```

---

## Troubleshooting

### Script not executable
```bash
chmod +x DEMO.sh test_kitten.sh
```

### Python not found
Make sure Python 3 is installed:
```bash
python3 --version
```

### Colors not showing
Make sure you're using a terminal that supports ANSI colors (most modern terminals do).

---

## Features to Verify

| Feature | Test Command | Expected |
|---------|-------------|----------|
| Index column | `echo -e "A\tB\n1\t2" \| ./blx cat` | Cyan # column |
| Right-align numbers | Same as above | Numbers right-aligned |
| Green headers | Same as above | Headers in green bold |
| Box borders | Same as above | ╭─┬─╮ style borders |
| Column select | Add `--select A` | Only column A shown |
| Row filter | Add `--where B>0` | Only matching rows |
| Sorting | Add `--sort B` | Sorted by column B |
| Statistics | Add `--stats B` | Shows stats below table |
| Combined ops | Add multiple flags | All work together |

All features should work exactly as shown in the Nushell screenshot you provided! 🎉

