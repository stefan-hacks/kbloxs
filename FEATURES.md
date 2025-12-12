# Advanced Features Added

## Nushell-Inspired Structured Data Operations

The blocks kitten now includes powerful structured data operations inspired by Nushell, while maintaining **full compatibility** with all existing commands and their flags.

## What Was Added

### 1. Column Selection (`--select`, `-s`)
Select specific columns from table output:
- Supports column names (case-insensitive, partial matching)
- Supports column indices
- Multiple columns comma-separated

### 2. Row Filtering (`--where`, `-w`)
Filter rows based on conditions:
- Exact match: `column=value`
- Numeric comparisons: `column>value`, `column<value`, etc.
- Pattern matching: `column~pattern` (regex)

### 3. Sorting (`--sort`)
Sort rows by any column:
- Automatic numeric/text detection
- Ascending by default
- Use `--reverse` or `-r` for descending

### 4. Statistics (`--stats`)
Calculate statistics for numeric columns:
- Count, sum, min, max, average
- Automatic numeric type detection

### 5. Limiting (`--limit`, `-n`)
Limit the number of rows displayed:
- Useful for "top N" queries
- Works with sorting for best results

## Implementation Details

### New Files
- `blocks_kitten/structured_data.py` - Core operations module
  - `TableOperations` class - Column/row operations
  - `DataTypeDetector` class - Type detection
  - `parse_operations()` function - Parse operation flags

### Modified Files
- `blocks_kitten/main.py` - Integrated operations
  - `separate_command_from_ops()` - Separates command args from operations
  - Enhanced `main()` function - Applies operations to tables
  - Added help system

## Key Design Decisions

### 1. Post-Processing Approach
Operations are applied **after** command execution, not during. This means:
- ✅ All command flags work exactly as normal
- ✅ No breaking changes to existing usage
- ✅ Commands execute with their native behavior

### 2. Smart Argument Separation
The system automatically separates:
- Command arguments (passed to command)
- Operation flags (processed by blx)

Use `--` if you need explicit separation (rare).

### 3. Type-Aware Operations
- Automatic type detection (int, float, string, filesize, etc.)
- Smart numeric comparisons
- Type-appropriate sorting

### 4. Flexible Column Matching
- Case-insensitive
- Partial matching (e.g., `USER` matches `USERNAME`)
- Index-based selection also supported

## Usage Patterns

### Simple Operations
```bash
blx ps aux --limit 10
blx df -h --sort Use%
```

### Combined Operations
```bash
blx ps aux \
    --select USER,PID,COMMAND \
    --where USER=root \
    --sort PID \
    --limit 5
```

### Complex Queries
```bash
# Top 5 memory-consuming processes
blx ps aux \
    --where "RSS>100000" \
    --select USER,PID,RSS,COMMAND \
    --sort RSS \
    --reverse \
    --limit 5
```

## Compatibility

✅ **100% backward compatible**
- All existing commands work exactly as before
- No changes needed to existing scripts
- Operations are opt-in via flags

✅ **Command flags preserved**
- `ps aux` - works normally
- `ls -la` - works normally  
- `docker ps -a` - works normally
- All flags/options passed through unchanged

## Testing

All operations tested with:
- `ps aux` - Process lists
- `df -h` - Disk usage
- `ls -la` - File listings
- `docker ps` - Container lists
- Complex multi-flag commands

## Future Enhancements

Potential additions (not yet implemented):
- Pipeline operations (chain multiple operations)
- Group by operations
- Aggregate functions
- Column transformations
- Export formats (JSON, CSV)
- Interactive mode

## Documentation

- `README.md` - Updated with basic examples
- `blocks_kitten/ADVANCED.md` - Detailed operation guide
- `--help` flag - Inline help system

