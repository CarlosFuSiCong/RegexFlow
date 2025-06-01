# app/utils/normalize_column_reference.py

import re
import pandas as pd


def normalize_column_reference(df: pd.DataFrame, col_ref: str) -> int:
    """
    Normalize a column reference to a zero-based column index.
    Supports:
      - digit string (e.g. "0", "3")
      - Excel-style letter(s) (e.g. "A", "Z", "AA")
      - column name (case-insensitive match)
    Raises ValueError if no match is found.
    """
    ref = col_ref.strip()

    # Case 1: purely digits -> numeric index
    if ref.isdigit():
        idx = int(ref)
        if idx < 0 or idx >= len(df.columns):
            raise ValueError(f"Column index {idx} is out of range")
        return idx

    # Case 2: letters only -> Excel column letter
    if re.fullmatch(r"[A-Za-z]+", ref):
        # Convert to uppercase and compute index
        letters = ref.upper()
        idx = 0
        for ch in letters:
            idx = idx * 26 + (ord(ch) - ord("A") + 1)
        idx -= 1
        if idx < 0 or idx >= len(df.columns):
            raise ValueError(f"Column letter '{ref}' out of range")
        return idx

    # Case 3: treat as column name (case-insensitive)
    lower_map = {col.lower(): idx for idx, col in enumerate(df.columns)}
    if ref.lower() in lower_map:
        return lower_map[ref.lower()]

    raise ValueError(f"Cannot normalize column reference: '{col_ref}'")
