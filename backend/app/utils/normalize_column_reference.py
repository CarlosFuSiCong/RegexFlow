import re
import pandas as pd
from app.utils.target_resolver import column_letter_to_index


def normalize_column_reference(df: pd.DataFrame, col_ref: str) -> int:
    """
    Convert a column reference to a column index (int).
    Supports:
    - "0", "2" → column index
    - "A", "B" → Excel letter
    - "Email" → if matches column name
    Returns: column index (int)
    """
    col_ref = col_ref.strip()

    # Case 1: numeric string index
    if col_ref.isdigit():
        idx = int(col_ref)
        if 0 <= idx < len(df.columns):
            return idx

    # Case 2: Excel-style letter
    if re.fullmatch(r"[A-Za-z]+", col_ref):
        idx = column_letter_to_index(col_ref.upper())
        if 0 <= idx < len(df.columns):
            return idx

    # Case 3: column name
    if col_ref in df.columns:
        return df.columns.get_loc(col_ref)

    raise ValueError(f"Unrecognized column reference: {col_ref}")
