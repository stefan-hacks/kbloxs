# Installation Guide

## Super Simple Installation

Just run:

```bash
./install.sh
```

Then reload your shell:

```bash
source ~/.bashrc
```

That's it! You're ready to use `blx` or `b` commands.

## What Gets Installed

The installer automatically:

1. ✅ Installs the kitten to `~/.config/kitty/kittens/blocks_kitten/`
2. ✅ Creates the `blx` command in `~/.local/bin/`
3. ✅ Adds `b` alias to your `~/.bashrc` or `~/.bash_aliases`
4. ✅ Adds helpful comment to `kitty.conf`
5. ✅ Makes all files executable

## Usage After Installation

### Option 1: Use `blx` (always available)

```bash
blx ls -la
blx ps aux
blx git status
```

### Option 2: Use `b` alias (after reloading shell)

```bash
b ls -la
b ps aux
b git status
```

## Verification

After installation, test it:

```bash
# Test blx
blx echo "Hello, World!"

# Test b alias (after source ~/.bashrc)
b echo "Test successful!"
```

## Manual Installation Steps

If you prefer to install manually:

### Step 1: Install Kitten

```bash
mkdir -p ~/.config/kitty/kittens
cp -r blocks_kitten ~/.config/kitty/kittens/
chmod +x ~/.config/kitty/kittens/blocks_kitten/main.py
```

### Step 2: Install blx Command

```bash
mkdir -p ~/.local/bin
cp blx ~/.local/bin/
chmod +x ~/.local/bin/blx
```

### Step 3: Add to PATH

Add this line to `~/.bashrc` (if not already there):

```bash
export PATH="${HOME}/.local/bin:$PATH"
```

### Step 4: Add b Alias

Add this line to `~/.bashrc` or `~/.bash_aliases`:

```bash
alias b='blx'
```

### Step 5: Reload Shell

```bash
source ~/.bashrc
```

## System-Wide Installation

For system-wide installation (requires sudo):

```bash
# Install kitten system-wide
sudo cp -r blocks_kitten /usr/lib/kitty/kittens/
sudo chmod +x /usr/lib/kitty/kittens/blocks_kitten/main.py

# Install blx system-wide
sudo cp blx /usr/local/bin/
sudo chmod +x /usr/local/bin/blx
```

## Uninstallation

To remove the kitten:

```bash
# Remove kitten
rm -rf ~/.config/kitty/kittens/blocks_kitten

# Remove blx command
rm ~/.local/bin/blx

# Remove alias from ~/.bashrc or ~/.bash_aliases
# Edit the file and remove the line: alias b='blx'
```

## Troubleshooting

### blx command not found

Check if `~/.local/bin` is in your PATH:

```bash
echo $PATH | grep -q "$HOME/.local/bin" && echo "OK" || echo "Missing"
```

If missing, add to `~/.bashrc`:

```bash
export PATH="${HOME}/.local/bin:$PATH"
```

### b alias not working

Check if alias exists:

```bash
alias b
```

If not, reload your shell:

```bash
source ~/.bashrc
```

### Kitten not found

Verify installation:

```bash
ls ~/.config/kitty/kittens/blocks_kitten/main.py
```

If missing, run installer again:

```bash
./install.sh
```
