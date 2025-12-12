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
                # Use first line as headers, split by single space
                headers = lines[0].split()
                start_idx = 1
                
                # For ps aux and similar, skip "total" line if present
                if start_idx < len(lines) and lines[start_idx].strip().lower().startswith('total'):
                    start_idx += 1
                
                rows = []
                # Determine expected column count from header
                expected_cols = len(headers)
                
                for line in lines[start_idx:]:
                    # Split by single space, but handle quoted strings
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
    """Renders blocks and tables in the terminal"""
    
    def __init__(self, screen_width: int = 80):
        self.update_width(screen_width)
        
    def update_width(self, width: int):
        """Update screen width for dynamic resizing"""
        self.screen_width = max(20, width)  # Minimum width
        
    def render_block(self, block: Block) -> str:
        """Render a command block"""
        result = []
        width = self.screen_width - 2  # Account for borders
        
        # Top border with rounded corners
        result.append("╭" + "─" * width + "╮")
        
        # Command line
        cmd_line = f"$ {block.command}"
        # Truncate if too long
        if len(cmd_line) > width:
            cmd_line = cmd_line[:width-3] + "..."
        result.append(f"│ {cmd_line:<{width}}│")
        
        # Separator
        result.append("├" + "─" * width + "┤")
        
        # Output
        if block.is_table and block.table_data and block.table_headers:
            table_lines = self.render_table(block.table_headers, block.table_data)
            for line in table_lines:
                # Ensure line fits in width
                if len(line) > width:
                    line = line[:width-3] + "..."
                result.append(f"│ {line:<{width}}│")
        else:
            # Regular output
            output_lines = block.output.split('\n')
            for line in output_lines:
                # Handle long lines by wrapping
                while len(line) > width:
                    result.append(f"│ {line[:width]:<{width}}│")
                    line = line[width:]
                result.append(f"│ {line:<{width}}│")
        
        # Status line
        result.append("├" + "─" * width + "┤")
        status_symbol = "✓" if block.exit_code == 0 else "✗"
        status_color = "\033[32m" if block.exit_code == 0 else "\033[31m"  # Green or Red
        reset_color = "\033[0m"
        status_text = "Success" if block.exit_code == 0 else f"Error (exit code: {block.exit_code})"
        status_line = f"{status_color}{status_symbol}{reset_color} {status_text}"
        result.append(f"│ {status_line:<{width}}│")
        
        # Bottom border with rounded corners
        result.append("╰" + "─" * width + "╯")
        
        return '\n'.join(result)
    
    def render_table(self, headers: List[str], rows: List[List[str]]) -> List[str]:
        """Render a table with dynamic column widths"""
        if not headers or not rows:
            return []
        
        num_cols = len(headers)
        available_width = self.screen_width - 6  # Account for borders, padding, and separators
        
        # Calculate column widths based on content
        col_widths = []
        for header in headers:
            col_widths.append(len(str(header)))
        
        # Adjust based on data
        for row in rows:
            for i, cell in enumerate(row[:num_cols]):
                if i < len(col_widths):
                    col_widths[i] = max(col_widths[i], len(str(cell)))
        
        # Calculate total width needed
        total_width = sum(col_widths) + (len(col_widths) - 1) * 3  # 3 chars for " │ "
        
        # If too wide, scale down proportionally
        if total_width > available_width:
            scale = available_width / total_width
            col_widths = [max(int(w * scale), 3) for w in col_widths]
            
            # Recalculate to ensure we fit
            total_width = sum(col_widths) + (len(col_widths) - 1) * 3
            if total_width > available_width:
                # If still too wide, make equal widths
                equal_width = (available_width - (num_cols - 1) * 3) // num_cols
                col_widths = [max(equal_width, 3) for _ in range(num_cols)]
        
        result = []
        
        # Render header with styling
        header_parts = []
        for i, header in enumerate(headers):
            if i < len(col_widths):
                header_text = str(header)[:col_widths[i]]
                header_parts.append(header_text.ljust(col_widths[i]))
        result.append("\033[1m" + " │ ".join(header_parts) + "\033[0m")  # Bold headers
        
        # Separator line
        separator_parts = ["─" * w for w in col_widths]
        result.append("─┼─".join(separator_parts))
        
        # Render rows
        for row in rows:
            row_parts = []
            for i, cell in enumerate(row[:num_cols]):
                if i < len(col_widths):
                    cell_str = str(cell)[:col_widths[i]]
                    row_parts.append(cell_str.ljust(col_widths[i]))
            result.append(" │ ".join(row_parts))
        
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
        
        # Apply operations (Nushell-like features)
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
        block.metadata = {'stats': stats, 'operations': ops} if stats else {'operations': ops}
    
    # Render block and print it
    renderer = BlockRenderer(screen_width)
    rendered = renderer.render_block(block)
    print(rendered)
    
    # Print statistics if calculated
    if is_table and ops['stats'] and block.metadata and block.metadata.get('stats'):
        stats = block.metadata['stats']
        print(f"\n📊 Statistics for column '{ops['stats']}':")
        print(f"   Count: {stats['count']}")
        print(f"   Sum: {stats['sum']:.2f}")
        print(f"   Min: {stats['min']:.2f}")
        print(f"   Max: {stats['max']:.2f}")
        print(f"   Avg: {stats['avg']:.2f}")


def print_help():
    """Print help message"""
    help_text = """
╔════════════════════════════════════════════════════════════════╗
║              Blocks Kitten (blx) - Nushell-like                ║
║              Structured Data Operations                        ║
╚════════════════════════════════════════════════════════════════╝

Usage:
    blx <command> [command-args...] [operations...]

Examples:
    blx ls -la
    blx ps aux --select USER,PID,COMMAND
    blx ps aux --where USER=root --sort PID
    blx df -h --where "Use%>80" --sort Use%
    blx docker ps --limit 10

Operations (Nushell-inspired):
    --select, -s COLUMNS      Select specific columns
                              Example: --select USER,PID,COMMAND
    
    --where, -w CONDITION     Filter rows based on condition
                              Operators: = != > < >= <= ~
                              Example: --where USER=root
                              Example: --where "PID>1000"
                              Example: --where COMMAND~python
    
    --sort COLUMN             Sort by column (ascending)
                              Example: --sort PID
    
    --reverse, -r             Reverse sort order
    
    --stats COLUMN            Show statistics for numeric column
                              Example: --stats RSS
    
    --limit, -n N             Limit number of rows shown
                              Example: --limit 10

Notes:
    • All normal command flags/options work as usual
    • Operations are applied after command execution
    • Use -- to separate operations from command args if needed
    • Column names are matched case-insensitively and partially

    """
    print(help_text)


def handle_result(args: List[str], answer: str, target_window_id: int, boss: Any) -> None:
    """Handle the result - this is called by kitty after main()"""
    pass


if __name__ == '__main__':
    # When run directly (not as a kitty kitten)
    main()

