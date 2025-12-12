#!/usr/bin/env python3
"""
Kitty Kitten for Block and Tabular Styled Output
Provides Nushell-like block and table rendering for command output

Usage:
    kitty +kitten blocks_kitten <command> [args...]
    kitty +kitten blocks_kitten ls -la
    kitty +kitten blocks_kitten ps aux
    kitty +kitten blocks_kitten git status
"""

import sys
import subprocess
import shlex
import re
import os
import signal
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from itertools import zip_longest

# ANSI Color Codes for beautiful output
class Colors:
    """ANSI color codes for terminal output"""
    # Reset
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    
    # Text colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    # Bright colors
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"
    
    # Background colors
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"
    
    # Nushell-like color scheme
    HEADER_BG = BG_BLUE
    HEADER_FG = BRIGHT_WHITE
    INDEX_COLOR = BRIGHT_CYAN
    BORDER_COLOR = BRIGHT_BLACK
    SUCCESS_COLOR = BRIGHT_GREEN
    ERROR_COLOR = BRIGHT_RED
    COMMAND_COLOR = BRIGHT_CYAN
    SEPARATOR_COLOR = BRIGHT_BLACK
    
    @staticmethod
    def colorize(text: str, color: str) -> str:
        """Apply color to text"""
        return f"{color}{text}{Colors.RESET}"
    
    @staticmethod
    def bold(text: str) -> str:
        """Make text bold"""
        return f"{Colors.BOLD}{text}{Colors.RESET}"
    
    @staticmethod
    def strip_ansi(text: str) -> str:
        """Strip ANSI codes from text for length calculation"""
        return re.sub(r'\033\[[0-9;]*m', '', text)

# Import structured data operations
try:
    from .structured_data import (
        TableOperations,
        DataTypeDetector,
        parse_operations,
        ColumnType
    )
except ImportError:
    # When running directly (not as package), add current directory to path
    import os
    import sys
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    import structured_data
    TableOperations = structured_data.TableOperations
    DataTypeDetector = structured_data.DataTypeDetector
    parse_operations = structured_data.parse_operations
    ColumnType = structured_data.ColumnType

# Try to import kitty modules (available when running in kitty)
try:
    from kitty.fast_data_types import get_options
    from kitty.rgb import color_as_int
    KITTY_AVAILABLE = True
except ImportError:
    KITTY_AVAILABLE = False


@dataclass
class Block:
    """Represents a command block with input and output"""
    command: str
    output: str
    exit_code: int
    is_table: bool = False
    table_data: Optional[List[List[str]]] = None
    table_headers: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class TableDetector:
    """Detects if output is tabular data and parses it"""
    
    @staticmethod
    def is_tabular(output: str) -> bool:
        """Check if output appears to be tabular data"""
        lines = [l for l in output.strip().split('\n') if l.strip()]
        if len(lines) < 2:
            return False
        
        # Check for common table patterns
        # 1. Multiple spaces separating columns (common in Unix tools like ls -l, df)
        space_separated = False
        for line in lines[:min(10, len(lines))]:
            if re.search(r'\s{2,}', line):
                space_separated = True
                break
        
        # 2. Tab-separated
        tab_separated = any('\t' in line for line in lines[:min(10, len(lines))])
        
        # 3. Pipe-separated
        pipe_separated = any('|' in line and line.count('|') >= 2 for line in lines[:min(10, len(lines))])
        
        # 4. CSV-like (comma separated with consistent column count)
        csv_like = False
        if lines and ',' in lines[0]:
            col_count = lines[0].count(',') + 1
            if col_count > 1:
                csv_like = all((line.count(',') + 1 == col_count) for line in lines[1:min(10, len(lines))] if line.strip())
        
        # 5. Single-space separated with consistent word count (like ps aux)
        # Only if we have a header-like first line and consistent structure
        single_space_table = False
        if len(lines) >= 3 and not (space_separated or tab_separated or pipe_separated or csv_like):
            # Check if first line looks like headers (all caps, short words)
            first_line_words = lines[0].split()
            if len(first_line_words) >= 5:
                # Check if most lines have similar word counts
                word_counts = [len(line.split()) for line in lines[1:min(20, len(lines))]]
                if word_counts:
                    avg_count = sum(word_counts) / len(word_counts)
                    # If 80% of lines have word count within 1 of average, likely a table
                    similar_count = sum(1 for count in word_counts if abs(count - avg_count) <= 1)
                    if similar_count / len(word_counts) >= 0.8:
                        single_space_table = True
        
        return space_separated or tab_separated or pipe_separated or csv_like or single_space_table
    
    @staticmethod
    def parse_table(output: str) -> Tuple[List[str], List[List[str]]]:
        """Parse tabular data into headers and rows"""
        lines = [line for line in output.strip().split('\n') if line.strip()]
        if not lines:
            return [], []
        
        # Determine separator
        first_line = lines[0]
        separator = None
        
        if '\t' in first_line:
            separator = '\t'
        elif '|' in first_line and first_line.count('|') >= 2:
            separator = '|'
            # Clean up pipe separators (remove leading/trailing pipes and spaces)
            lines = [line.strip().strip('|').strip() for line in lines if line.strip()]
        elif ',' in first_line and first_line.count(',') >= 2:
            separator = ','
        else:
            # Space-separated with multiple spaces (2+ spaces)
            separator = None
        
        if separator:
            # Split by separator
            headers = [col.strip() for col in lines[0].split(separator) if col.strip()]
            if not headers:
                # If no headers extracted, try to infer from first data row
                if len(lines) > 1:
                    first_data = [col.strip() for col in lines[1].split(separator) if col.strip()]
                    headers = [f"Column {i+1}" for i in range(len(first_data))]
            
            rows = []
            start_idx = 1 if headers else 0
            for line in lines[start_idx:]:
                cols = [col.strip() for col in line.split(separator) if col.strip()]
                if cols:
                    rows.append(cols)
        else:
            # Space-separated
            # Check if it's single-space (like ps aux) or multiple-space separated
            first_line_spaces = re.split(r'\s{2,}', lines[0].strip())
            
            if len(first_line_spaces) > 1:
                # Multiple spaces (2+) - use as-is
                headers = first_line_spaces
                start_idx = 1
                rows = []
                for line in lines[start_idx:]:
                    cols = re.split(r'\s{2,}', line.strip())
                    if cols and len(cols) > 1:
                        rows.append(cols)
                    elif cols and len(cols) == 1 and len(rows) > 0:
                        # Might be continuation of previous row (filename with spaces)
                        if rows:
                            rows[-1][-1] += " " + cols[0]
            else:
                # Single-space separated (like ps aux)
                # Use first line as headers, split by whitespace
                headers = lines[0].split()
                start_idx = 1
                
                # For ls -l and similar, skip "total" line if present
                if start_idx < len(lines) and lines[start_idx].strip().lower().startswith('total'):
                    start_idx += 1
                
                rows = []
                # Determine expected column count from header
                expected_cols = len(headers)
                
                # Debug: print headers to understand structure
                # print(f"DEBUG: Headers ({len(headers)}): {headers}", file=sys.stderr)
                
                # Special handling for ps aux style output (last column is COMMAND which can have spaces)
                # Split each line by whitespace, but merge last columns if needed
                for line in lines[start_idx:]:
                    # Split by whitespace
                    parts = line.split()
                    
                    if len(parts) >= expected_cols:
                        # If we have more parts than headers, merge the extra parts into the last column
                        # For ps aux: USER PID %CPU %MEM VSZ RSS TTY STAT START TIME COMMAND
                        # That's 11 columns, so merge everything after column 10 into COMMAND
                        cols = parts[:expected_cols-1] + [' '.join(parts[expected_cols-1:])]
                        rows.append(cols)
                    elif len(parts) == expected_cols:
                        # Perfect match
                        rows.append(parts)
                    elif len(parts) > 0 and len(parts) >= expected_cols - 2:
                        # Close enough - pad with empty strings
                        cols = parts + [''] * (expected_cols - len(parts))
                        rows.append(cols)
                    else:
                        # Fallback: simple split by space
                        cols = []
                        current_col = ""
                        in_quotes = False
                        
                        for char in line:
                            if char == '"' or char == "'":
                                in_quotes = not in_quotes
                                current_col += char
                            elif char == ' ' and not in_quotes:
                                if current_col:
                                    cols.append(current_col)
                                    current_col = ""
                            else:
                                current_col += char
                        
                        if current_col:
                            cols.append(current_col)
                        
                        # If we got close to expected columns, use it
                        if cols and abs(len(cols) - expected_cols) <= 2:
                            # Pad or truncate to match header count
                            if len(cols) < expected_cols:
                                cols = cols + [''] * (expected_cols - len(cols))
                            elif len(cols) > expected_cols:
                                # Merge last columns if too many (command with spaces)
                                cols = cols[:expected_cols-1] + [' '.join(cols[expected_cols-1:])]
                            rows.append(cols)
        
        # Normalize column counts
        if headers:
            max_cols = len(headers)
            normalized_rows = []
            for row in rows:
                # Pad or truncate to match header count
                normalized_row = row[:max_cols]
                if len(normalized_row) < max_cols:
                    normalized_row = normalized_row + [''] * (max_cols - len(normalized_row))
                normalized_rows.append(normalized_row)
            rows = normalized_rows
        else:
            rows = []
        
        return headers, rows


class BlockRenderer:
    """Renders tables in pure Nushell style"""
    
    def __init__(self, screen_width: int = 80):
        self.update_width(screen_width)
        
    def update_width(self, width: int):
        """Update screen width for dynamic resizing"""
        self.screen_width = max(20, width)  # Minimum width
        
    def render_block(self, block: Block) -> str:
        """Render output in Nushell style (table only, no wrapper)"""
        # For tables, render as pure Nushell table (no wrapper block)
        if block.is_table and block.table_data and block.table_headers:
            table_lines = self.render_table(block.table_headers, block.table_data)
            return '\n'.join(table_lines)
        else:
            # For non-table output, just return the output as-is
            return block.output
    
    def render_table(self, headers: List[str], rows: List[List[str]]) -> List[str]:
        """Render a table in pure Nushell format with exact box-drawing characters
        
        Nushell table format:
        ╭────┬──────────┬──────┬─────────┬───────────────╮
        │ #  │   name   │ type │  size   │   modified    │
        ├────┼──────────┼──────┼─────────┼───────────────┤
        │  0 │ .cargo   │ dir  │     0 B │ 9 minutes ago │
        │  1 │ assets   │ dir  │     0 B │ 2 weeks ago   │
        ╰────┴──────────┴──────┴─────────┴───────────────╯
        """
        if not headers or not rows:
            return []
        
        # Add index column (#) like Nushell
        index_header = "#"
        indexed_headers = [index_header] + headers
        indexed_rows = [[str(i)] + row for i, row in enumerate(rows, start=0)]
        
        num_cols = len(indexed_headers)
        
        # Detect numeric columns for right-alignment (like Nushell)
        is_numeric_col = [False] * num_cols
        is_numeric_col[0] = True  # Index column is always numeric and right-aligned
        for col_idx in range(1, num_cols):
            # Check if most values in this column are numeric
            numeric_count = 0
            total_count = 0
            for row in indexed_rows:
                if col_idx < len(row) and row[col_idx].strip():
                    total_count += 1
                    val = row[col_idx].strip()
                    # Check if numeric (int, float, size with units, percentages)
                    test_val = val.replace('.', '').replace(',', '').replace('-', '').replace('+', '').replace('%', '').replace(' ', '')
                    for unit in ['kB', 'MB', 'GB', 'TB', 'B', 'KiB', 'MiB', 'GiB', 'TiB']:
                        test_val = test_val.replace(unit, '')
                    if test_val.isdigit():
                        numeric_count += 1
            if total_count > 0 and numeric_count / total_count > 0.7:
                is_numeric_col[col_idx] = True
        
        # Calculate column widths based on content
        col_widths = []
        for col_idx in range(num_cols):
            max_width = len(indexed_headers[col_idx])
            for row in indexed_rows:
                if col_idx < len(row):
                    max_width = max(max_width, len(str(row[col_idx])))
            col_widths.append(max_width)
        
        result = []
        
        # Top border: ╭─┬─┬─╮ (Nushell style)
        border_parts = []
        for w in col_widths:
            border_parts.append("─" * (w + 2))  # +2 for padding spaces
        top_border = "╭" + "┬".join(border_parts) + "╮"
        result.append(Colors.colorize(top_border, Colors.BRIGHT_BLACK))
        
        # Header row: │ # │ name │ ... │
        header_parts = []
        for i, header in enumerate(indexed_headers):
            header_text = str(header)
            if len(header_text) > col_widths[i]:
                header_text = header_text[:col_widths[i]]
            
            # Right-align numeric columns, left-align others (but center headers)
            header_padded = header_text.center(col_widths[i])
            
            # Color headers - green for all (Nushell style)
            header_colored = Colors.colorize(Colors.bold(header_padded), Colors.BRIGHT_GREEN)
            header_parts.append(header_colored)
        
        border_char = Colors.colorize("│", Colors.BRIGHT_BLACK)
        result.append(f"{border_char} " + f" {border_char} ".join(header_parts) + f" {border_char}")
        
        # Middle border: ├─┼─┼─┤ (Nushell style)
        border_parts = []
        for w in col_widths:
            border_parts.append("─" * (w + 2))  # +2 for padding spaces
        middle_border = "├" + "┼".join(border_parts) + "┤"
        result.append(Colors.colorize(middle_border, Colors.BRIGHT_BLACK))
        
        # Data rows: │ 0 │ .cargo │ ... │
        for row_idx, row in enumerate(indexed_rows):
            row_parts = []
            for i, cell in enumerate(row[:num_cols]):
                cell_str = str(cell) if i < len(row) else ""
                if len(cell_str) > col_widths[i]:
                    cell_str = cell_str[:col_widths[i]]
                
                # Right-align numeric columns, left-align text
                if is_numeric_col[i]:
                    cell_padded = cell_str.rjust(col_widths[i])
                else:
                    cell_padded = cell_str.ljust(col_widths[i])
                
                # Color the cell
                if i == 0:  # Index column - cyan
                    cell_colored = Colors.colorize(cell_padded, Colors.BRIGHT_CYAN)
                else:
                    # Alternating row colors for readability
                    if row_idx % 2 == 0:
                        cell_colored = cell_padded
                    else:
                        cell_colored = Colors.colorize(cell_padded, Colors.DIM)
                
                row_parts.append(cell_colored)
            
            border_char = Colors.colorize("│", Colors.BRIGHT_BLACK)
            result.append(f"{border_char} " + f" {border_char} ".join(row_parts) + f" {border_char}")
        
        # Bottom border: ╰─┴─┴─╯ (Nushell style)
        border_parts = []
        for w in col_widths:
            border_parts.append("─" * (w + 2))  # +2 for padding spaces
        bottom_border = "╰" + "┴".join(border_parts) + "╯"
        result.append(Colors.colorize(bottom_border, Colors.BRIGHT_BLACK))
        
        return result


def get_terminal_size() -> int:
    """Get terminal width"""
    try:
        import shutil
        size = shutil.get_terminal_size()
        return size.columns
    except:
        return 80


def run_command(cmd: List[str]) -> Tuple[str, int]:
    """Execute a command and return output and exit code"""
    try:
        # Set up environment
        env = os.environ.copy()
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
            env=env
        )
        
        # Use stdout if available, otherwise stderr
        output = result.stdout if result.stdout else result.stderr
        return output, result.returncode
    except subprocess.TimeoutExpired:
        return "Command timed out after 5 minutes", 124
    except FileNotFoundError:
        return f"Command not found: {cmd[0]}", 127
    except Exception as e:
        return f"Error executing command: {str(e)}", 1


def separate_command_from_ops(args: List[str]) -> Tuple[List[str], Dict[str, Any]]:
    """Separate command arguments from blx operation flags"""
    # blx operation flags
    op_flags = ['--select', '-s', '--where', '-w', '--sort', '--reverse', '-r', 
                '--stats', '--limit', '-n', '--help', '-h']
    
    command = []
    ops = parse_operations(args)
    
    # Find where command starts (after any operation flags)
    i = 0
    skip_next = False
    while i < len(args):
        arg = args[i]
        if skip_next:
            skip_next = False
            i += 1
            continue
        
        # Check if it's an operation flag
        if arg in op_flags:
            # Skip this flag and potentially next arg
            if arg in ['--select', '-s', '--where', '-w', '--sort', '--stats', '--limit', '-n']:
                skip_next = True
            i += 1
        elif arg == '--':
            # Everything after -- is part of the command
            command.extend(args[i+1:])
            break
        else:
            # This is part of the command
            command.append(arg)
            i += 1
    
    return command, ops


def main(args: List[str] = None) -> None:
    """
    Main entry point for the kitten - called by kitty
    Uses sys.argv directly when called by kitty, or accepts args when called directly
    """
    # When called by kitty, sys.argv contains the full command line
    # When called directly, args might be provided
    if args is None:
        # Called by kitty - use sys.argv
        # sys.argv[0] is the script name, sys.argv[1:] are the arguments
        if len(sys.argv) < 2:
            print("Usage: kitty +kitten blocks_kitten <command> [args...] [--select columns] [--where condition] [--sort column]")
            print("Example: kitty +kitten blocks_kitten ps aux --select USER,PID,COMMAND")
            print("Example: kitty +kitten blocks_kitten ps aux --where USER=root --sort PID")
            sys.exit(1)
        all_args = sys.argv[1:]
    else:
        # Called directly with args
        if len(args) < 1:
            print("Usage: blocks_kitten <command> [args...] [--select columns] [--where condition] [--sort column]")
            sys.exit(1)
        all_args = args
    
    # Show help if requested
    if '--help' in all_args or '-h' in all_args:
        print_help()
        sys.exit(0)
    
    # Separate command from operations
    command, ops = separate_command_from_ops(all_args)
    
    if not command:
        print("Error: No command specified")
        print("Usage: blx <command> [args...] [operations...]")
        print("Use --help for more information")
        sys.exit(1)
    
    # Get terminal size
    screen_width = get_terminal_size()
    
    # Execute command (with its normal flags/options)
    output, exit_code = run_command(command)
    
    # Detect if output is tabular
    detector = TableDetector()
    is_table = detector.is_tabular(output)
    
    block = Block(
        command=" ".join(shlex.quote(arg) for arg in command),
        output=output,
        exit_code=exit_code,
        is_table=is_table,
        metadata={}
    )
    
    # Parse table if detected
    if is_table:
        headers, rows = detector.parse_table(output)
        
        # Store original headers/rows for index operations
        original_headers = headers.copy()
        original_rows = rows.copy()
        
        # Apply operations (Nushell-like features)
        # Note: Index column (#) will be added during rendering, but operations
        # can reference columns by index (0-based) or by name
        if ops['select']:
            headers, rows = TableOperations.select_columns(headers, rows, ops['select'])
        
        if ops['where']:
            rows = TableOperations.filter_rows(headers, rows, ops['where'])
        
        if ops['sort']:
            rows = TableOperations.sort_rows(headers, rows, ops['sort'], ops['reverse'])
        
        if ops['limit']:
            rows = rows[:ops['limit']]
        
        # Calculate statistics if requested
        stats = None
        if ops['stats']:
            stats = TableOperations.get_column_stats(headers, rows, ops['stats'])
        
        block.table_headers = headers
        block.table_data = rows
        block.metadata = {
            'stats': stats, 
            'operations': ops,
            'original_headers': original_headers,
            'original_rows': original_rows
        } if stats else {
            'operations': ops,
            'original_headers': original_headers,
            'original_rows': original_rows
        }
    
    # Render block and print it
    renderer = BlockRenderer(screen_width)
    rendered = renderer.render_block(block)
    print(rendered)
    
    # Print statistics if calculated (colorized)
    if is_table and ops['stats'] and block.metadata and block.metadata.get('stats'):
        stats = block.metadata['stats']
        stats_title = Colors.colorize(
            f"\n📊 Statistics for column '{ops['stats']}':",
            Colors.BOLD + Colors.BRIGHT_YELLOW
        )
        print(stats_title)
        
        stats_items = [
            ("Count", stats['count'], Colors.BRIGHT_CYAN),
            ("Sum", f"{stats['sum']:.2f}", Colors.BRIGHT_GREEN),
            ("Min", f"{stats['min']:.2f}", Colors.BRIGHT_BLUE),
            ("Max", f"{stats['max']:.2f}", Colors.BRIGHT_MAGENTA),
            ("Avg", f"{stats['avg']:.2f}", Colors.BRIGHT_YELLOW),
        ]
        
        for label, value, color in stats_items:
            label_colored = Colors.colorize(f"   {label}:", Colors.BOLD + Colors.WHITE)
            value_colored = Colors.colorize(str(value), color)
            print(f"{label_colored} {value_colored}")


def print_help():
    """Print beautiful colorized help message"""
    # Title
    title = Colors.colorize(
        "╔════════════════════════════════════════════════════════════════╗\n"
        "║              Blocks Kitten (blx) - Nushell-like                ║\n"
        "║              Structured Data Operations                        ║\n"
        "╚════════════════════════════════════════════════════════════════╝",
        Colors.BRIGHT_CYAN
    )
    print(title)
    print()
    
    # Usage section
    usage_title = Colors.colorize("Usage:", Colors.BOLD + Colors.BRIGHT_YELLOW)
    usage_cmd = Colors.colorize("    blx <command> [command-args...] [operations...]", Colors.BRIGHT_WHITE)
    print(f"{usage_title}\n{usage_cmd}\n")
    
    # Examples section
    examples_title = Colors.colorize("Examples:", Colors.BOLD + Colors.BRIGHT_YELLOW)
    print(examples_title)
    examples = [
        ("    blx ls -la", Colors.BRIGHT_GREEN),
        ("    blx ps aux --select USER,PID,COMMAND", Colors.BRIGHT_GREEN),
        ("    blx ps aux --where USER=root --sort PID", Colors.BRIGHT_GREEN),
        ("    blx df -h --where \"Use%>80\" --sort Use%", Colors.BRIGHT_GREEN),
        ("    blx docker ps --limit 10", Colors.BRIGHT_GREEN),
    ]
    for example, color in examples:
        print(Colors.colorize(example, color))
    print()
    
    # Operations section
    ops_title = Colors.colorize("Operations (Nushell-inspired):", Colors.BOLD + Colors.BRIGHT_YELLOW)
    print(ops_title)
    
    operations = [
        {
            "flag": "--select, -s COLUMNS",
            "desc": "Select specific columns (supports column names or indices)",
            "example": "--select USER,PID,COMMAND or --select 0,1,2",
            "color": Colors.BRIGHT_CYAN
        },
        {
            "flag": "--where, -w CONDITION",
            "desc": "Filter rows based on condition",
            "example": "--where USER=root or --where \"PID>1000\" or --where COMMAND~python",
            "color": Colors.BRIGHT_CYAN
        },
        {
            "flag": "--sort COLUMN",
            "desc": "Sort by column (ascending)",
            "example": "--sort PID or --sort 1 (by index)",
            "color": Colors.BRIGHT_CYAN
        },
        {
            "flag": "--reverse, -r",
            "desc": "Reverse sort order",
            "example": "--sort PID --reverse",
            "color": Colors.BRIGHT_CYAN
        },
        {
            "flag": "--stats COLUMN",
            "desc": "Show statistics for numeric column",
            "example": "--stats RSS or --stats 2 (by index)",
            "color": Colors.BRIGHT_CYAN
        },
        {
            "flag": "--limit, -n N",
            "desc": "Limit number of rows shown",
            "example": "--limit 10 or -n 5",
            "color": Colors.BRIGHT_CYAN
        },
    ]
    
    for op in operations:
        flag_colored = Colors.colorize(f"    {op['flag']}", Colors.BOLD + op['color'])
        desc_colored = Colors.colorize(f"      {op['desc']}", Colors.WHITE)
        example_colored = Colors.colorize(f"      Example: {op['example']}", Colors.DIM + Colors.BRIGHT_BLACK)
        print(f"{flag_colored}\n{desc_colored}\n{example_colored}\n")
    
    # Operators section
    operators_title = Colors.colorize("Where Operators:", Colors.BOLD + Colors.BRIGHT_YELLOW)
    print(operators_title)
    operators = [
        ("    =", "Equals"),
        ("    !=", "Not equals"),
        ("    >", "Greater than (numeric)"),
        ("    <", "Less than (numeric)"),
        ("    >=", "Greater than or equal"),
        ("    <=", "Less than or equal"),
        ("    ~", "Pattern match (regex)"),
    ]
    for op, desc in operators:
        op_colored = Colors.colorize(op, Colors.BRIGHT_MAGENTA)
        desc_colored = Colors.colorize(desc, Colors.WHITE)
        print(f"{op_colored}  {desc_colored}")
    print()
    
    # Features section
    features_title = Colors.colorize("Features:", Colors.BOLD + Colors.BRIGHT_YELLOW)
    print(features_title)
    features = [
        Colors.colorize("    ✓", Colors.BRIGHT_GREEN) + " Index column (#) for row referencing",
        Colors.colorize("    ✓", Colors.BRIGHT_GREEN) + " Beautiful colorized output",
        Colors.colorize("    ✓", Colors.BRIGHT_GREEN) + " Dynamic table formatting",
        Colors.colorize("    ✓", Colors.BRIGHT_GREEN) + " Column selection by name or index",
        Colors.colorize("    ✓", Colors.BRIGHT_GREEN) + " Row filtering with multiple operators",
        Colors.colorize("    ✓", Colors.BRIGHT_GREEN) + " Sorting and statistics",
        Colors.colorize("    ✓", Colors.BRIGHT_GREEN) + " All command flags work as usual",
    ]
    for feature in features:
        print(feature)
    print()
    
    # Notes section
    notes_title = Colors.colorize("Notes:", Colors.BOLD + Colors.BRIGHT_YELLOW)
    print(notes_title)
    notes = [
        Colors.colorize("    •", Colors.BRIGHT_CYAN) + " All normal command flags/options work as usual",
        Colors.colorize("    •", Colors.BRIGHT_CYAN) + " Operations are applied after command execution",
        Colors.colorize("    •", Colors.BRIGHT_CYAN) + " Use -- to separate operations from command args if needed",
        Colors.colorize("    •", Colors.BRIGHT_CYAN) + " Column names are matched case-insensitively and partially",
        Colors.colorize("    •", Colors.BRIGHT_CYAN) + " Index column (#) allows referencing rows by number",
        Colors.colorize("    •", Colors.BRIGHT_CYAN) + " Tables are automatically detected and formatted",
    ]
    for note in notes:
        print(note)
    print()
    
    # Footer
    footer = Colors.colorize(
        "For more information, visit: https://github.com/your-repo/kbloxs",
        Colors.DIM + Colors.BRIGHT_BLACK
    )
    print(footer)


def handle_result(args: List[str], answer: str, target_window_id: int, boss: Any) -> None:
    """Handle the result - this is called by kitty after main()"""
    pass


if __name__ == '__main__':
    # When run directly (not as a kitty kitten)
    main()

