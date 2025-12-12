# Blocks Kitten

A Kitty terminal kitten that provides Nushell-like block and tabular styled output for any command.

## Features

- **Block-style output**: Commands are displayed in visually distinct blocks with rounded borders
- **Automatic table detection**: Detects tabular data and renders it as formatted tables
- **Dynamic table sizing**: Tables automatically adapt to terminal width
- **Support for all commands**: Works with any command and its flags/options
- **Color-coded status**: Visual indicators for command success/failure
- **Multiple table formats**: Supports space-separated, tab-separated, pipe-separated, and CSV-like data

## Installation

1. Copy the `blocks_kitten` directory to your kitty kittens directory:
   ```bash
   cp -r blocks_kitten ~/.config/kitty/kittens/blocks_kitten
   ```

   Or if kitty is installed system-wide:
   ```bash
   sudo cp -r blocks_kitten /usr/lib/kitty/kittens/blocks_kitten
   ```

2. Make sure the files are executable:
   ```bash
   chmod +x ~/.config/kitty/kittens/blocks_kitten/main.py
   ```

## Usage

Run any command through the blocks kitten:

```bash
# List files with block styling
kitty +kitten blocks_kitten ls -la

# Process list with table formatting
kitty +kitten blocks_kitten ps aux

# Git status
kitty +kitten blocks_kitten git status

# Any command with its options
kitty +kitten blocks_kitten df -h
kitty +kitten blocks_kitten docker ps
kitty +kitten blocks_kitten systemctl list-units
```

## How It Works

1. The kitten executes the command you specify
2. It analyzes the output to detect if it's tabular data
3. If tabular, it parses the data into headers and rows
4. The output is rendered in a block with:
   - The command at the top
   - Formatted output (table or text) in the middle
   - Status indicator at the bottom

## Table Detection

The kitten automatically detects tables by looking for:
- Multiple spaces between columns (common in Unix tools like `ps`, `ls -l`)
- Tab-separated values
- Pipe-separated values (`|`)
- CSV-like comma-separated values

## Examples

### Space-separated table (ps aux)
```bash
kitty +kitten blocks_kitten ps aux
```

### Git status
```bash
kitty +kitten blocks_kitten git status
```

### System information
```bash
kitty +kitten blocks_kitten systemctl list-units --type=service
```

## Customization

You can modify the rendering in `main.py`:
- Change border characters
- Adjust colors
- Modify table formatting
- Change column width calculations

## Requirements

- Kitty terminal
- Python 3.6+

## License

MIT License

