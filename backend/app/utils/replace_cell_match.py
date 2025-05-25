# app/utils/replace_cell_match.py

import pandas as pd
import re
import logging
from typing import List, Dict, Union

logger = logging.getLogger(__name__)


def replace_cell_match(
    df: pd.DataFrame,
    cell_label: str,
    pattern: str,
    replacement: str,
    inplace: bool = False,
) -> Dict[str, Union[pd.DataFrame, List[Dict]]]:

    try:
        regex = re.compile(pattern)
    except re.error as e:
        logger.error(f"Invalid regex pattern: {e}")
        raise ValueError(f"Invalid regex pattern: {e}")

    col_part = "".join(filter(str.isalpha, cell_label)).upper()
    row_part = "".join(filter(str.isdigit, cell_label))

    if not col_part or not row_part:
        raise ValueError(f"Invalid cell label format: '{cell_label}'")

    row_idx = int(row_part) - 1  # Excel-style, so subtract 1
    col_idx = ord(col_part) - ord("A")

    if row_idx >= len(df) or col_idx >= len(df.columns):
        raise ValueError(f"Cell '{cell_label}' is out of bounds.")

    column_name = df.columns[col_idx]

    if not inplace:
        df = df.copy()

    original = str(df.iat[row_idx, col_idx])
    try:
        new_val = regex.sub(replacement, original)
        if new_val != original:
            df.iat[row_idx, col_idx] = new_val
            return {
                "updated_df": df,
                "replacements": [
                    {
                        "row": row_idx,
                        "column": column_name,
                        "from": original,
                        "to": new_val,
                    }
                ],
            }
        else:
            logger.info(f"No match found in cell {cell_label}.")
            raise ValueError(f"No match found in cell {cell_label}.")
    except Exception as e:
        logger.exception("Error occurred during cell regex replacement.")
        raise RuntimeError("Error occurred during replacement process.") from e
