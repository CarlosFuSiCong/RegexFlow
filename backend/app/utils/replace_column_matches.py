# app/utils/replace_column_matches.py

import re
import pandas as pd
import logging
from typing import List, Dict
from app.utils.regex_utils import convert_dollar_groups_to_python


logger = logging.getLogger(__name__)


def replace_column_matches(
    df: pd.DataFrame,
    column_name: str,
    pattern: str,
    replacement: str,
    inplace: bool = False,
) -> Dict:
    """
    Replace regex matches in a specific column. Returns:
      {
        "updated_df": df,
        "replacements": [ { "row": r, "column": column_name, "original": o, "modified": m }, ... ]
      }
    """
    if not inplace:
        df = df.copy()

    if column_name not in df.columns:
        raise ValueError(f"Column '{column_name}' does not exist.")

    replacements: List[Dict] = []
    regex = re.compile(pattern)
    replacement = convert_dollar_groups_to_python(replacement)

    for r in range(len(df)):
        original = df.at[r, column_name]
        if pd.isnull(original):
            continue
        orig_str = str(original)
        new_str = regex.sub(replacement, orig_str)
        if new_str != orig_str:
            df.at[r, column_name] = new_str
            replacements.append(
                {
                    "row": r,
                    "column": column_name,
                    "original": orig_str,
                    "modified": new_str,
                }
            )

    return {"updated_df": df, "replacements": replacements}
