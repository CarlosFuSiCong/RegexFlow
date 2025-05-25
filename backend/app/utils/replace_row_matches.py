# app/utils/replace_row_matches.py

import pandas as pd
import re
import logging
from typing import List, Dict, Union

logger = logging.getLogger(__name__)


def replace_row_matches(
    df: pd.DataFrame,
    row_index: int,
    pattern: str,
    replacement: str,
    inplace: bool = False,
) -> Dict[str, Union[pd.DataFrame, List[Dict]]]:

    try:
        regex = re.compile(pattern)
    except re.error as e:
        logger.error(f"Invalid regex pattern: {e}")
        raise ValueError(f"Invalid regex pattern: {e}")

    if row_index >= len(df) or row_index < 0:
        raise ValueError(f"Row index '{row_index}' is out of bounds.")

    if not inplace:
        df = df.copy()

    replacements = []
    try:
        for col in df.columns:
            original = str(df.at[row_index, col])
            new_val = regex.sub(replacement, original)
            if new_val != original:
                df.at[row_index, col] = new_val
                replacements.append(
                    {"row": row_index, "column": col, "from": original, "to": new_val}
                )
    except Exception as e:
        logger.exception("Error occurred during row regex replacement.")
        raise RuntimeError("Error occurred during replacement process.") from e

    if not replacements:
        logger.info(f"No matches found in row {row_index}.")
        raise ValueError(f"No matches found in row {row_index}.")

    logger.info(f"Total replacements in row {row_index}: {len(replacements)}")
    return {"updated_df": df, "replacements": replacements}
