import re
import pandas as pd
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)


def resolve_target(df: pd.DataFrame, target: str) -> List[Tuple[int, int]]:
    """
    Convert semantic target into list of (row, col) coordinates.
    Supports:
    - "row 3"
    - "column Email"
    - "cell 1,2"
    - "column Email rows 1 to 2"
    - "row 1 columns 0 to 2"
    - "range A1:C3"

    Now also matches column names in a case‐insensitive manner.
    """
    # Build a mapping of lowercase column names to the actual column names for case-insensitive lookup
    lower_to_actual = {c.lower(): c for c in df.columns}

    target_clean = target.strip().lower()

    # 1. Match "row N"
    if m := re.fullmatch(r"row\s+(\d+)", target_clean):
        row = int(m.group(1))
        if row < 0 or row >= len(df):
            raise ValueError(f"Row index '{row}' is out of bounds.")
        return [(row, c) for c in range(len(df.columns))]

    # 2. Match "column NAME"
    if m := re.fullmatch(r"column\s+(.+)", target_clean):
        col_key = m.group(1).strip()  # Already lowercase
        if col_key not in lower_to_actual:
            raise ValueError(
                f"Column '{m.group(1).strip()}' not found (case‐insensitive lookup failed)."
            )
        actual_col = lower_to_actual[col_key]
        col_index = df.columns.get_loc(actual_col)
        return [(r, col_index) for r in range(len(df))]

    # 2b. Match "column N" where N is a digit (index-based access)
    if m := re.fullmatch(r"column\s+(\d+)", target_clean):
        col_index = int(m.group(1))
        if col_index < 0 or col_index >= len(df.columns):
            raise ValueError(f"Column index '{col_index}' is out of bounds.")
        return [(r, col_index) for r in range(len(df))]

    # 3. Match "cell R,C"
    if m := re.fullmatch(r"cell\s+(\d+)\s*,\s*(\d+)", target_clean):
        r, c = int(m.group(1)), int(m.group(2))
        if r < 0 or r >= len(df) or c < 0 or c >= len(df.columns):
            raise ValueError(f"Cell coordinates ({r},{c}) out of bounds.")
        return [(r, c)]

    # 4. Match "column NAME rows R1 to R2"
    if m := re.fullmatch(r"column\s+(.+)\s+rows\s+(\d+)\s+to\s+(\d+)", target_clean):
        col_key = m.group(1).strip()
        r1, r2 = int(m.group(2)), int(m.group(3))
        if col_key not in lower_to_actual:
            raise ValueError(
                f"Column '{m.group(1).strip()}' not found (case‐insensitive lookup failed)."
            )
        if r1 < 0 or r2 >= len(df) or r1 > r2:
            raise ValueError(f"Invalid row range {r1} to {r2}.")
        actual_col = lower_to_actual[col_key]
        col_index = df.columns.get_loc(actual_col)
        return [(r, col_index) for r in range(r1, r2 + 1)]

    # 5. Match "row R1 columns C1 to C2"
    if m := re.fullmatch(r"row\s+(\d+)\s+columns\s+(\d+)\s+to\s+(\d+)", target_clean):
        row = int(m.group(1))
        c1, c2 = int(m.group(2)), int(m.group(3))
        if row < 0 or row >= len(df) or c1 < 0 or c2 >= len(df.columns) or c1 > c2:
            raise ValueError(f"Invalid row/column range in target '{target}'.")
        return [(row, c) for c in range(c1, c2 + 1)]

    # 6. Match "range A1:C3" (supports "a1:c3", "A1:C3", etc.)
    if m := re.fullmatch(r"range\s+([a-z]+)(\d+):([a-z]+)(\d+)", target_clean):
        c1, r1, c2, r2 = m.groups()
        # Excel row numbers start from 1, convert to 0-based index for DataFrame
        r1_idx, r2_idx = int(r1) - 1, int(r2) - 1
        col_start = column_letter_to_index(c1.upper())
        col_end = column_letter_to_index(c2.upper())
        if (
            r1_idx < 0
            or r2_idx >= len(df)
            or r1_idx > r2_idx
            or col_start < 0
            or col_end >= len(df.columns)
            or col_start > col_end
        ):
            raise ValueError(f"Invalid Excel range '{m.group(0)}'.")
        return [
            (r, c)
            for r in range(r1_idx, r2_idx + 1)
            for c in range(col_start, col_end + 1)
        ]

    raise ValueError(f"Unrecognized target format: '{target}'")


def column_letter_to_index(col: str) -> int:
    """
    Convert Excel-style column letters (e.g., "A", "B", ..., "Z", "AA", "AB", ...)
    into a 0-based column index.
    """
    index = 0
    for char in col:
        index = index * 26 + (ord(char.upper()) - ord("A") + 1)
    return index - 1
