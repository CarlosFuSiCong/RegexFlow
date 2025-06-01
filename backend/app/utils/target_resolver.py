# app/utils/target_resolver.py

import re
import pandas as pd
import logging

from typing import List, Tuple

logger = logging.getLogger(__name__)


def column_letter_to_index(col_letter: str) -> int:
    """
    Convert an Excel-style column letter (e.g., "A", "Z", "AA") to a zero-based index.
    """
    col_letter = col_letter.upper()
    index = 0
    for char in col_letter:
        if not ("A" <= char <= "Z"):
            raise ValueError(f"Invalid column letter: '{col_letter}'")
        index = index * 26 + (ord(char) - ord("A") + 1)
    return index - 1


def resolve_target(df: pd.DataFrame, target: str) -> List[Tuple[int, int]]:
    """
    Given a DataFrame and a target string (already trimmed, not lowercased),
    return a list of (row_index, col_index) tuples that match that target.
    Raises ValueError if the format is unrecognized or indices are out of range.
    Supported formats:
      - "cell <Letters><Digits>"        (e.g. "B2", "AA10")
      - "range <Letters><Digits>:<Letters><Digits>"  (e.g. "A1:C3")
      - "row <N> columns <C1> to <C2>"  (e.g. "row 2 columns 1 to 4")
      - "column <C> rows <R1> to <R2>"  (e.g. "column B rows 0 to 3")
    """
    raw = target.strip()

    # CASE A: single cell like "B2"
    if m := re.fullmatch(r"(?i)cell\s+([A-Za-z]+)(\d+)", raw):
        col_letters = m.group(1).upper()
        row_str = m.group(2)
        row_index = int(row_str) - 1
        col_index = column_letter_to_index(col_letters)
        _validate_cell(df, row_index, col_index)
        return [(row_index, col_index)]

    # CASE B: range like "range A1:C3"
    if m := re.fullmatch(r"(?i)range\s+([A-Za-z]+)(\d+):([A-Za-z]+)(\d+)", raw):
        start_col = m.group(1).upper()
        start_row = int(m.group(2)) - 1
        end_col = m.group(3).upper()
        end_row = int(m.group(4)) - 1
        c1 = column_letter_to_index(start_col)
        c2 = column_letter_to_index(end_col)
        coords = []
        for r in range(min(start_row, end_row), max(start_row, end_row) + 1):
            for c in range(min(c1, c2), max(c1, c2) + 1):
                _validate_cell(df, r, c)
                coords.append((r, c))
        return coords

    # CASE C: "row N columns C1 to C2"
    if m := re.fullmatch(r"(?i)row\s+(\d+)\s+columns\s+(\d+)\s+to\s+(\d+)", raw):
        row_index = int(m.group(1)) - 1
        c1 = int(m.group(2))
        c2 = int(m.group(3))
        coords = []
        for c in range(min(c1, c2), max(c1, c2) + 1):
            _validate_cell(df, row_index, c)
            coords.append((row_index, c))
        return coords

    # CASE D: "column C rows R1 to R2"
    if m := re.fullmatch(
        r"(?i)column\s+([A-Za-z]+|\d+)\s+rows\s+(\d+)\s+to\s+(\d+)", raw
    ):
        col_ref = m.group(1)
        r1 = int(m.group(2))
        r2 = int(m.group(3))
        # Determine if col_ref is letter or digit
        if col_ref.isdigit():
            col_index = int(col_ref)
        else:
            col_index = column_letter_to_index(col_ref.upper())
        coords = []
        for r in range(min(r1, r2), max(r1, r2) + 1):
            _validate_cell(df, r, col_index)
            coords.append((r, col_index))
        return coords

    # Unrecognized format
    raise ValueError(f"Unrecognized target format: '{target}'")


def _validate_cell(df: pd.DataFrame, row: int, col: int):
    """
    Ensure that (row, col) indexes are within DataFrame bounds.
    """
    if row < 0 or row >= len(df):
        raise ValueError(f"Row index {row} out of range (0 to {len(df)-1})")
    if col < 0 or col >= len(df.columns):
        raise ValueError(f"Column index {col} out of range (0 to {len(df.columns)-1})")
