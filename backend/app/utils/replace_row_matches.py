# app/utils/replace_row_matches.py

import re
import pandas as pd
import logging
from typing import List, Dict
from app.utils.regex_utils import convert_dollar_groups_to_python


logger = logging.getLogger(__name__)


def replace_row_matches(
    df: pd.DataFrame,
    row_index: int,
    pattern: str,
    replacement: str,
    inplace: bool = False,
) -> Dict:
    """
    Replace regex matches in all columns of a specific row. Returns:
      {
        "updated_df": df,
        "replacements": [ { "row": row_index, "column": c_name, "original": o, "modified": m }, ... ]
      }
    """
    if not inplace:
        df = df.copy()

    if row_index < 0 or row_index >= len(df):
        raise ValueError(f"Row index {row_index} is out of range.")

    replacements: List[Dict] = []
    regex = re.compile(pattern)
    replacement = convert_dollar_groups_to_python(replacement)

    for c in df.columns:
        original = df.at[row_index, c]
        if pd.isnull(original):
            continue
        orig_str = str(original)
        new_str = regex.sub(replacement, orig_str)
        if new_str != orig_str:
            df.at[row_index, c] = new_str
            replacements.append(
                {
                    "row": row_index,
                    "column": c,
                    "original": orig_str,
                    "modified": new_str,
                }
            )

    return {"updated_df": df, "replacements": replacements}
