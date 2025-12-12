# Advanced Features - Nushell-inspired Operations

The blocks kitten now supports structured data operations inspired by Nushell, while maintaining full compatibility with all normal command flags and options.

## Key Principle

**All normal command flags and options work exactly as before!**

The new operations are applied **after** your command executes, so they don't interfere with how commands work.

## Operations

### Column Selection (`--select`, `-s`)

Select only specific columns from table output:

```bash
# Show only user, PID, and command columns
blx ps aux --select USER,PID,COMMAND

# Select specific columns from df output
blx df -h --select Filesystem,Size,Avail

# Column names are matched case-insensitively and partially
blx docker ps --select ID,IMAGE,STATUS
```

### Row Filtering (`--where`, `-w`)

Filter rows based on conditions:

```bash
# Filter by exact match
blx ps aux --where USER=root

# Numeric comparisons
blx ps aux --where "PID>1000"
blx df -h --where "Use%>=80"

# Pattern matching (regex)
blx ps aux --where COMMAND~python
blx ps aux --where COMMAND~".*nginx.*"

# Multiple conditions (use standard shell piping if needed)
blx ps aux --where USER=root | blx --where "PID>1000"
```

**Supported operators:**
- `=` - Equals
- `!=` - Not equals  
- `>` - Greater than (numeric)
- `<` - Less than (numeric)
- `>=` - Greater than or equal
- `<=` - Less than or equal
- `~` - Pattern match (regex)

### Sorting (`--sort`)

Sort rows by a column:

```bash
# Sort by PID
blx ps aux --sort PID

# Sort by memory usage
blx ps aux --sort RSS

# Reverse sort order
blx ps aux --sort PID --reverse
blx ps aux --sort PID -r

# Sort disk usage
blx df -h --sort Use%
```

### Limiting Results (`--limit`, `-n`)

Limit the number of rows displayed:

```bash
# Show only first 10 processes
blx ps aux --limit 10

# Top 5 memory consumers
blx ps aux --sort RSS --reverse --limit 5

# Short form
blx docker ps -n 5
```

### Statistics (`--stats`)

Get statistics for numeric columns:

```bash
# Memory statistics
blx ps aux --stats RSS

# CPU statistics
blx ps aux --stats %CPU

# Disk usage statistics
blx df -h --stats Use%
```

Statistics include: count, sum, min, max, average

## Combining Operations

You can combine multiple operations:

```bash
# Select columns, filter, sort, and limit
blx ps aux \
    --select USER,PID,%CPU,COMMAND \
    --where USER=root \
    --sort %CPU \
    --reverse \
    --limit 10

# Find processes using most memory
blx ps aux \
    --where "RSS>100000" \
    --select USER,PID,RSS,COMMAND \
    --sort RSS \
    --reverse \
    --limit 5
```

## Examples

### Process Management

```bash
# Find all Python processes
blx ps aux --where COMMAND~python

# Top CPU consumers
blx ps aux --sort %CPU --reverse --limit 5

# Processes by specific user
blx ps aux --where USER=www-data --select PID,COMMAND

# Process memory statistics
blx ps aux --stats RSS
```

### Disk Usage

```bash
# Filesystems with >80% usage
blx df -h --where "Use%>80"

# Sorted by usage
blx df -h --sort Use% --reverse

# Show only size columns
blx df -h --select Filesystem,Size,Used,Avail,Use%
```

### Docker

```bash
# Running containers only
blx docker ps --where STATUS=Up

# Show specific columns
blx docker ps --select ID,IMAGE,PORTS,STATUS

# Limit results
blx docker ps --limit 10
```

### System Services

```bash
# Running services
blx systemctl list-units --type=service --where Active=running

# Failed services
blx systemctl list-units --type=service --where Active=failed
```

## How It Works

1. **Command executes normally** with all its flags/options
2. **Output is captured** and analyzed
3. **If tabular**, operations are applied:
   - Table is parsed into headers and rows
   - Operations are applied in order:
     1. Column selection (`--select`)
     2. Row filtering (`--where`)
     3. Sorting (`--sort`)
     4. Limiting (`--limit`)
4. **Result is rendered** in a beautiful block

## Separating Operations from Command Args

If you need to separate operations from command arguments (rare), use `--`:

```bash
blx ps --sort PID -- aux
```

Normally this isn't needed since operations are detected automatically.

## Comparison to Nushell

Like Nushell:
- ✅ Structured data operations
- ✅ Column selection and filtering
- ✅ Sorting and statistics
- ✅ Type-aware operations

Unlike Nushell:
- ✅ **Works with ANY command** - no new syntax to learn
- ✅ **All command flags work** - compatibility preserved
- ✅ **Post-processing** - operations apply after execution
- ✅ **No breaking changes** - existing usage continues to work

## Tips

1. **Column names** are matched case-insensitively and support partial matching
2. **Numeric comparisons** work automatically when values are numeric
3. **Pattern matching** (`~`) uses regex - escape special characters if needed
4. **Operations order matters**: select → filter → sort → limit
5. **Use quotes** for values with spaces or special characters

