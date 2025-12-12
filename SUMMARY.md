# Blocks Kitten - Summary

## What It Does

Transforms any command output into beautiful, structured blocks with automatic table formatting - inspired by Nushell.

## Installation

```bash
./install.sh
source ~/.bashrc
```

## Usage

### Simple: Just prefix with 'b'
```bash
b ls -la
b ps aux
b git status
```

### Alternative: Use 'blx'
```bash
blx ls -la
blx ps aux
blx git status
```

## What Gets Installed

1. **Kitten**: `~/.config/kitty/kittens/blocks_kitten/`
2. **blx command**: `~/.local/bin/blx`
3. **b alias**: Added to `~/.bashrc` or `~/.bash_aliases`
4. **kitty.conf**: Updated with helpful comments

## Files

- `blocks_kitten/` - Main kitten code
- `blx` - Wrapper script (installed to ~/.local/bin/)
- `install.sh` - Installation script
- `README.md` - Full documentation
- `QUICKSTART.md` - Quick reference
- `INSTALL.md` - Installation details

## Key Features

- ✅ Automatic table detection and formatting
- ✅ Dynamic resizing to terminal width
- ✅ Works with any command and all flags/options
- ✅ Beautiful block styling
- ✅ Status indicators (✓/✗)
- ✅ Super simple: just prefix with `b`

## Quick Examples

```bash
b ls -la          # File listing
b ps aux          # Process list (table)
b git status      # Git status
b docker ps       # Docker containers
b df -h           # Disk usage (table)
b <any-command>   # Works with everything!
```

That's it! Simple and powerful. 🚀

