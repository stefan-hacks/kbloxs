# Blocks Kitten (blx) - Nushell-like Block Output for Kitty Terminal

Transform any command's output into beautiful, structured blocks with automatic table formatting - just like Nushell!

## 🚀 Quick Start

### 1. Install (One Command)

```bash
./install.sh
```

That's it! The installer will:
- ✅ Install the kitten
- ✅ Create the `blx` command
- ✅ Add the `b` alias to your shell
- ✅ Set up everything automatically

### 2. Reload Your Shell

```bash
source ~/.bashrc
# or just open a new terminal
```

### 3. Use It!

```bash
blx ls -la          # Long form
b ls -la            # Short alias (just prefix with 'b')
b ps aux            # Process list
b git status        # Git status
b docker ps         # Docker containers
b df -h             # Disk usage
```

## 📖 Usage Examples

### Basic Commands

```bash
# List files with block styling
b ls -la

# Process list (automatically formatted as table)
b ps aux

# Git status
b git status

# Docker containers
b docker ps

# System services
b systemctl list-units --type=service

# Disk usage (table format)
b df -h

# Any command works!
b <your-command> [args...]
```

### Advanced Operations (Nushell-inspired)

**All normal command flags still work!** Operations are applied after command execution.

```bash
# Select specific columns
b ps aux --select USER,PID,COMMAND

# Filter rows (find root processes)
b ps aux --where USER=root

# Sort by column
b ps aux --sort %CPU --reverse

# Limit results (top 10)
b ps aux --limit 10

# Combine operations (top 5 CPU consumers)
b ps aux --select USER,PID,%CPU,COMMAND --sort %CPU --reverse --limit 5

# Get statistics
b ps aux --stats RSS

# Filter disk usage (>80% used)
b df -h --where "Use%>80" --sort Use% --reverse
```

See [ADVANCED.md](blocks_kitten/ADVANCED.md) for detailed documentation.

### What You Get

Every command is wrapped in a beautiful block with:
- 📦 **Command display** at the top
- 📊 **Automatic table detection** (if output is tabular)
- 📏 **Dynamic sizing** (adapts to terminal width)
- ✅ **Status indicator** (✓ for success, ✗ for errors)
- 🎨 **Clean formatting** with borders and colors

## 🎯 Features

- **✨ Block-style output** - Visual blocks for each command
- **🔍 Automatic table detection** - Detects and formats tabular data
- **📐 Dynamic resizing** - Tables adapt to your terminal width
- **🛠️ Works with any command** - All flags and options work normally
- **⚡ Fast and lightweight** - No external dependencies
- **🎨 Color-coded status** - Green ✓ for success, red ✗ for errors
- **🔬 Nushell-inspired operations** - Select, filter, sort, and analyze table data
  - Column selection (`--select`)
  - Row filtering (`--where`)  
  - Sorting (`--sort`)
  - Statistics (`--stats`)
  - Limiting (`--limit`)

## 📋 Commands

### `blx` Command (Recommended)

The `blx` command works reliably in all cases:

```bash
blx <command> [args...]
```

**How it works:**
- In Kitty terminal: Uses `kitty +kitten blocks_kitten`
- Otherwise: Runs Python directly (works everywhere!)

Examples:
```bash
blx ls -la
blx ps aux
blx git status
```

### `b` Alias (Short Form)

The installer adds a `b` alias - just prefix any command with `b`:

```bash
b ls -la
b ps aux
b git status
```

**Note:** The `b` alias is added to your `~/.bashrc` or `~/.bash_aliases`. Reload your shell after installation to use it.

### Using with `kitty +kitten` (Optional)

You can also use the kitten directly (requires Kitty terminal):

```bash
kitty +kitten blocks_kitten ls -la
```

**Note:** If you get "No kitten named blocks_kitten", just use `blx` instead - it works the same way!

## 🔧 Installation Details

The installer (`./install.sh`) does the following:

1. **Installs the kitten** to `~/.config/kitty/kittens/blocks_kitten/`
2. **Creates `blx` command** in `~/.local/bin/blx`
3. **Adds `b` alias** to your `~/.bashrc` or `~/.bash_aliases`
4. **Updates kitty.conf** (adds helpful comment)

### Manual Installation

If you prefer manual installation:

```bash
# 1. Install kitten
mkdir -p ~/.config/kitty/kittens
cp -r blocks_kitten ~/.config/kitty/kittens/
chmod +x ~/.config/kitty/kittens/blocks_kitten/main.py

# 2. Install blx command
mkdir -p ~/.local/bin
cp blx ~/.local/bin/
chmod +x ~/.local/bin/blx

# 3. Add to PATH (if not already)
echo 'export PATH="${HOME}/.local/bin:$PATH"' >> ~/.bashrc

# 4. Add alias
echo "alias b='blx'" >> ~/.bashrc

# 5. Reload shell
source ~/.bashrc
```

## 🧪 Testing

Test that everything works:

```bash
# Test blx command
blx echo "Hello, World!"

# Test b alias (after reloading shell)
b echo "Test successful!"

# Test with table output
b ps aux | head -15
```

## 🎨 Table Detection

The kitten automatically detects and formats:

- **Space-separated** (multiple spaces) - `ls -l`, `df -h`
- **Single-space separated** - `ps aux`, `netstat`
- **Tab-separated** values
- **Pipe-separated** (`|`)
- **CSV-like** comma-separated values

Tables automatically resize to fit your terminal width!

## ✅ Verification

After installation, verify everything works:

```bash
# Run the verification script
./verify_install.sh

# Or test manually
blx echo "Hello, World!"
b echo "Test alias"
```

## ❓ Troubleshooting

### `blx: command not found`

The installer should add `~/.local/bin` to your PATH automatically. If it's missing:

```bash
export PATH="${HOME}/.local/bin:$PATH"
```

Add this to your `~/.bashrc` if it's missing, then reload:
```bash
source ~/.bashrc
```

### `b: command not found`

The `b` alias is added during installation. Reload your shell:

```bash
source ~/.bashrc
```

Or check if it exists:
```bash
grep "alias b=" ~/.bashrc ~/.bash_aliases
```

### Kitten not found

Check if the kitten is installed:

```bash
ls ~/.config/kitty/kittens/blocks_kitten/
```

If missing, run the installer again:
```bash
./install.sh
```

### Colors not showing

Colors use ANSI codes and should work in most terminals. The kitten works without colors too - formatting is the main feature.

## 📚 How It Works

1. **You run:** `b ls -la` or `blx ls -la`
2. **The kitten executes:** the command you specified
3. **It analyzes:** the output to detect if it's tabular data
4. **It formats:** the output into a beautiful block with:
   - Command display at the top
   - Formatted table or text output
   - Status indicator at the bottom

## 🔄 Comparison to Nushell

Like Nushell, this kitten provides:
- ✅ Structured data visualization
- ✅ Automatic table detection
- ✅ Clean block separation
- ✅ Consistent formatting

But unlike Nushell:
- ✅ Works with **any existing command** - no new syntax to learn
- ✅ **Preserves all command semantics** - flags and options work normally
- ✅ **Kitty terminal extension** - integrates with your workflow
- ✅ **Super simple** - just prefix with `b` or use `blx`

## 📝 Requirements

- **Kitty terminal** (https://sw.kovidgoyal.net/kitty/)
- **Python 3.6+**
- **Bash** (for the alias)

## 🎯 Quick Reference

```bash
# Installation
./install.sh
source ~/.bashrc

# Usage (long form)
blx <command> [args...] [operations...]

# Usage (short form - preferred)
b <command> [args...] [operations...]

# Basic examples
b ls -la
b ps aux
b git status
b docker ps
b df -h

# Advanced examples (Nushell-like operations)
b ps aux --select USER,PID,COMMAND --where USER=root --limit 5
b df -h --where "Use%>80" --sort Use% --reverse
b ps aux --sort %CPU --reverse --limit 10
b docker ps --select ID,IMAGE,STATUS

# Help
b --help
blx --help
```

**Operations:**
- `--select, -s COLUMNS` - Select columns
- `--where, -w CONDITION` - Filter rows  
- `--sort COLUMN` - Sort by column
- `--reverse, -r` - Reverse sort
- `--stats COLUMN` - Show statistics
- `--limit, -n N` - Limit rows

**Important:** All normal command flags and options work exactly as before!

## 📄 License

MIT License

---

**Enjoy beautiful, structured command output! 🎉**
