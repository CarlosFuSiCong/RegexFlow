# app/utils/replace_all_matches.py

import re
import pandas as pd
import logging
from typing import List, Dict
from app.utils.regex_utils import convert_dollar_groups_to_python


logger = logging.getLogger(__name__)


def replace_all_matches(
    df: pd.DataFrame, pattern: str, replacement: str, inplace: bool = False
) -> Dict:
    """
    Replace regex matches across the entire DataFrame. Returns:
      {
        "updated_df": df,
        "replacements": [ { "row": r, "column": c_name, "original": o, "modified": m }, ... ]
      }
    Raises ValueError if no matches found.
    """
    if not inplace:
        df = df.copy()

    replacements: List[Dict] = []
    regex = re.compile(pattern)
    replacement = convert_dollar_groups_to_python(replacement)

    for r in range(len(df)):
        for c in df.columns:
            original = df.at[r, c]
            if pd.isnull(original):
                continue
            orig_str = str(original)
            new_str = regex.sub(replacement, orig_str)
            if new_str != orig_str:
                df.at[r, c] = new_str
                replacements.append(
                    {"row": r, "column": c, "original": orig_str, "modified": new_str}
                )

    if not replacements:
        return {"updated_df": df, "replacements": []}
    return {"updated_df": df, "replacements": replacements}
