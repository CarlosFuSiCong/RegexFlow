# app/utils/replace_cell_match.py

import re
import pandas as pd
import logging
from typing import Dict

# Import the helper that converts Excel-style letters to zero-based index
from app.utils.target_resolver import column_letter_to_index
from app.utils.regex_utils import convert_dollar_groups_to_python


logger = logging.getLogger(__name__)


def replace_cell_match(
    df: pd.DataFrame,
    cell_label: str,
    pattern: str,
    replacement: str,
    inplace: bool = False,
) -> Dict:
    """
    Replace regex match in a single cell specified by Excel-style label (e.g., "B2").
    Returns:
      {
        "updated_df": df,
        "replacements": [ { "row": r, "column": c_name, "original": o, "modified": m } ]
      }
    """
    if not inplace:
        df = df.copy()

    # Parse cell_label into (letter part, digit part)
    if m := re.fullmatch(r"([A-Za-z]+)(\d+)", cell_label):
        col_letters = m.group(1).upper()
        row_number = int(m.group(2)) - 1
        # Convert column letters to zero-based index
        col_index = column_letter_to_index(col_letters)
    else:
        raise ValueError(f"Invalid cell label: '{cell_label}'")

    if row_number < 0 or row_number >= len(df):
        raise ValueError(f"Row index {row_number} out of range.")
    if col_index < 0 or col_index >= len(df.columns):
        raise ValueError(f"Column index {col_index} out of range.")

    column_name = df.columns[col_index]
    original = df.at[row_number, column_name]
    if pd.isnull(original):
        return {"updated_df": df, "replacements": []}

    orig_str = str(original)
    replacement_python = convert_dollar_groups_to_python(replacement)
    new_str = re.sub(pattern, replacement_python, orig_str)
    if new_str != orig_str:
        df.at[row_number, column_name] = new_str
        return {
            "updated_df": df,
            "replacements": [
                {
                    "row": row_number,
                    "column": column_name,
                    "original": orig_str,
                    "modified": new_str,
                }
            ],
        }

    return {"updated_df": df, "replacements": []}
