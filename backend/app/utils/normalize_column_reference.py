import re
import pandas as pd
from app.utils.target_resolver import column_letter_to_index


def normalize_column_reference(df: pd.DataFrame, col_ref: str) -> int:
    """
    Convert a column reference to a column index (int).
    Supports:
    - "0", "2" → numeric string index
    - "A", "B" → Excel-style letters
    - "Email" → column name (case-insensitive)
    Returns: column index (int)
    """
    col_ref = col_ref.strip()

    # Case 1: numeric string index
    if col_ref.isdigit():
        idx = int(col_ref)
        if 0 <= idx < len(df.columns):
            return idx

    # Case 2: Excel-style letters (e.g., "A", "AA")
    if re.fullmatch(r"[A-Za-z]+", col_ref):
        idx = column_letter_to_index(col_ref.upper())
        if 0 <= idx < len(df.columns):
            return idx

    # Case 3: column name (case-insensitive lookup)
    # Build a mapping from lowercase column names to actual names
    lower_to_actual = {c.lower(): c for c in df.columns}
    key = col_ref.lower()
    if key in lower_to_actual:
        actual_col = lower_to_actual[key]
        return df.columns.get_loc(actual_col)

    raise ValueError(f"Unrecognized column reference: {col_ref}")
