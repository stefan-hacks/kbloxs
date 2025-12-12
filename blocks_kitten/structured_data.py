"""
Structured data operations inspired by Nushell
Provides filtering, sorting, selecting, and transforming table data
"""

import re
from typing import List, Dict, Any, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum


class ColumnType(Enum):
    """Types of data in columns"""
    STRING = "string"
    INT = "int"
    FLOAT = "float"
    FILESIZE = "filesize"
    BOOL = "bool"
    DATE = "date"
    UNKNOWN = "unknown"


@dataclass
class TypedColumn:
    """Column with type information"""
    name: str
    type: ColumnType
    values: List[str]


class DataTypeDetector:
    """Detects data types in table columns"""
    
    @staticmethod
    def detect_type(values: List[str]) -> ColumnType:
        """Detect the type of a column based on its values"""
        if not values:
            return ColumnType.UNKNOWN
        
        # Check if all values are integers
        int_count = sum(1 for v in values if v.strip() and v.strip().replace('-', '').replace('+', '').isdigit())
        if int_count == len(values):
            return ColumnType.INT
        
        # Check if all values are floats
        float_count = 0
        for v in values:
            if v.strip():
                try:
                    float(v.strip().replace(',', ''))
                    float_count += 1
                except ValueError:
                    break
        
        # Check for filesize (contains MiB, KiB, GB, MB, KB, etc.)
        filesize_pattern = re.compile(r'\d+\.?\d*\s*(KiB|MiB|GiB|TiB|KB|MB|GB|TB|B)', re.IGNORECASE)
        filesize_count = sum(1 for v in values if filesize_pattern.search(v))
        if filesize_count > len(values) * 0.8:  # 80% match
            return ColumnType.FILESIZE
        
        # Check for boolean
        bool_values = {'true', 'false', 'yes', 'no', '1', '0', '✓', '✗', 'y', 'n'}
        bool_count = sum(1 for v in values if v.strip().lower() in bool_values)
        if bool_count > len(values) * 0.8:
            return ColumnType.BOOL
        
        # Check for date/time patterns
        date_patterns = [
            r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
            r'\d{2}/\d{2}/\d{4}',  # MM/DD/YYYY
            r'\d{2}:\d{2}:\d{2}',  # HH:MM:SS
        ]
        date_count = 0
        for pattern in date_patterns:
            date_count += sum(1 for v in values if re.search(pattern, v))
        if date_count > len(values) * 0.5:
            return ColumnType.DATE
        
        # Default to string
        return ColumnType.STRING
    
    @staticmethod
    def parse_filesize(value: str) -> Optional[float]:
        """Parse filesize string to bytes"""
        if not value:
            return None
        
        pattern = re.compile(r'(\d+\.?\d*)\s*(KiB|MiB|GiB|TiB|KB|MB|GB|TB|B)', re.IGNORECASE)
        match = pattern.search(value)
        if not match:
            return None
        
        size = float(match.group(1))
        unit = match.group(2).upper()
        
        multipliers = {
            'B': 1,
            'KB': 1000, 'MB': 1000**2, 'GB': 1000**3, 'TB': 1000**4,
            'KIB': 1024, 'MIB': 1024**2, 'GIB': 1024**3, 'TIB': 1024**4,
        }
        
        return size * multipliers.get(unit, 1)


class TableOperations:
    """Operations on structured table data"""
    
    @staticmethod
    def select_columns(headers: List[str], rows: List[List[str]], columns: List[str]) -> Tuple[List[str], List[List[str]]]:
        """Select specific columns from a table"""
        # Find column indices (avoid duplicates)
        selected_indices = []
        selected_headers = []
        used_indices = set()  # Track already selected indices
        
        for col in columns:
            col = col.strip()  # Remove whitespace
            # Support column name or index
            if col.isdigit():
                idx = int(col)
                if 0 <= idx < len(headers) and idx not in used_indices:
                    selected_indices.append(idx)
                    selected_headers.append(headers[idx])
                    used_indices.add(idx)
            else:
                # Try exact match first
                if col in headers:
                    idx = headers.index(col)
                    if idx not in used_indices:
                        selected_indices.append(idx)
                        selected_headers.append(col)
                        used_indices.add(idx)
                else:
                    # Try case-insensitive partial match
                    found = False
                    for i, h in enumerate(headers):
                        if i not in used_indices and col.lower() in h.lower():
                            selected_indices.append(i)
                            selected_headers.append(h)
                            used_indices.add(i)
                            found = True
                            break
        
        # Filter rows
        filtered_rows = []
        for row in rows:
            filtered_row = [row[i] if i < len(row) else '' for i in selected_indices]
            filtered_rows.append(filtered_row)
        
        return selected_headers, filtered_rows
    
    @staticmethod
    def filter_rows(headers: List[str], rows: List[List[str]], condition: str) -> List[List[str]]:
        """Filter rows based on a condition (column=value, column>value, etc.)"""
        if not condition:
            return rows
        
        # Parse condition (simple patterns)
        # Supports: column=value, column!=value, column>value, column<value, column~pattern
        pattern = re.compile(r'(\w+)\s*(=|!=|>|<|>=|<=|~)\s*(.+)')
        match = pattern.match(condition.strip())
        if not match:
            return rows
        
        col_name, op, value = match.groups()
        value = value.strip().strip('"').strip("'")
        
        # Find column index
        col_idx = -1
        for i, h in enumerate(headers):
            if col_name.lower() in h.lower():
                col_idx = i
                break
        
        if col_idx == -1:
            return rows
        
        filtered = []
        for row in rows:
            if col_idx >= len(row):
                continue
            
            cell_value = row[col_idx].strip()
            
            # Apply filter
            match = False
            if op == '=':
                match = cell_value.lower() == value.lower()
            elif op == '!=':
                match = cell_value.lower() != value.lower()
            elif op == '~':
                match = re.search(value, cell_value, re.IGNORECASE) is not None
            else:
                # Try numeric comparison
                try:
                    cell_num = float(cell_value.replace(',', ''))
                    value_num = float(value.replace(',', ''))
                    if op == '>':
                        match = cell_num > value_num
                    elif op == '<':
                        match = cell_num < value_num
                    elif op == '>=':
                        match = cell_num >= value_num
                    elif op == '<=':
                        match = cell_num <= value_num
                except ValueError:
                    pass
            
            if match:
                filtered.append(row)
        
        return filtered
    
    @staticmethod
    def sort_rows(headers: List[str], rows: List[List[str]], column: str, reverse: bool = False) -> List[List[str]]:
        """Sort rows by a column"""
        # Find column index
        col_idx = -1
        for i, h in enumerate(headers):
            if column.lower() in h.lower():
                col_idx = i
                break
        
        if col_idx == -1:
            return rows
        
        def sort_key(row):
            if col_idx >= len(row):
                return (0, '')  # Tuple for consistent comparison
            value = row[col_idx].strip()
            # Try numeric sort first
            try:
                num_val = float(value.replace(',', '').replace('%', ''))
                return (0, num_val)  # Numeric: type=0, value=number
            except ValueError:
                return (1, value.lower())  # String: type=1, value=string
        
        return sorted(rows, key=sort_key, reverse=reverse)
    
    @staticmethod
    def get_column_stats(headers: List[str], rows: List[List[str]], column: str) -> Dict[str, Any]:
        """Get statistics for a numeric column"""
        col_idx = -1
        for i, h in enumerate(headers):
            if column.lower() in h.lower():
                col_idx = i
                break
        
        if col_idx == -1:
            return {}
        
        values = []
        for row in rows:
            if col_idx < len(row):
                value = row[col_idx].strip()
                try:
                    values.append(float(value.replace(',', '')))
                except ValueError:
                    pass
        
        if not values:
            return {}
        
        return {
            'count': len(values),
            'sum': sum(values),
            'min': min(values),
            'max': max(values),
            'avg': sum(values) / len(values),
        }


def parse_operations(args: List[str]) -> Dict[str, Any]:
    """Parse operation flags from command arguments"""
    ops = {
        'select': None,  # Column selection
        'where': None,   # Row filtering
        'sort': None,    # Sorting
        'reverse': False,  # Reverse sort
        'stats': None,   # Column statistics
        'limit': None,   # Limit number of rows
    }
    
    i = 0
    while i < len(args):
        arg = args[i]
        
        if arg in ['--select', '-s'] and i + 1 < len(args):
            ops['select'] = args[i + 1].split(',')
            i += 2
        elif arg in ['--where', '-w'] and i + 1 < len(args):
            ops['where'] = args[i + 1]
            i += 2
        elif arg in ['--sort'] and i + 1 < len(args):
            ops['sort'] = args[i + 1]
            i += 2
        elif arg in ['--reverse', '-r']:
            ops['reverse'] = True
            i += 1
        elif arg in ['--stats'] and i + 1 < len(args):
            ops['stats'] = args[i + 1]
            i += 2
        elif arg in ['--limit', '-n'] and i + 1 < len(args):
            try:
                ops['limit'] = int(args[i + 1])
            except ValueError:
                pass
            i += 2
        else:
            i += 1
    
    return ops

