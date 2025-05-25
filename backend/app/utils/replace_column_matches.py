# app/utils/replace_column_matches.py

import pandas as pd
import re
import logging
from typing import List, Dict, Union

logger = logging.getLogger(__name__)


def replace_column_matches(
    df: pd.DataFrame,
    column_name: str,
    pattern: str,
    replacement: str,
    inplace: bool = False,
) -> Dict[str, Union[pd.DataFrame, List[Dict]]]:

    try:
        regex = re.compile(pattern)
    except re.error as e:
        logger.error(f"Invalid regex pattern: {e}")
        raise ValueError(f"Invalid regex pattern: {e}")

    if column_name not in df.columns:
        raise ValueError(f"Column '{column_name}' does not exist in the table.")

    if not inplace:
        df = df.copy()

    replacements = []
    try:
        for row_idx in range(len(df)):
            original = str(df.at[row_idx, column_name])
            new_val = regex.sub(replacement, original)
            if new_val != original:
                df.at[row_idx, column_name] = new_val
                replacements.append(
                    {
                        "row": row_idx,
                        "column": column_name,
                        "from": original,
                        "to": new_val,
                    }
                )
    except Exception as e:
        logger.exception("Error occurred during column regex replacement.")
        raise RuntimeError("Error occurred during replacement process.") from e

    if not replacements:
        logger.info(f"No matches found in column '{column_name}'.")
        raise ValueError(f"No matches found in column '{column_name}'.")

    logger.info(f"Total replacements in column '{column_name}': {len(replacements)}")
    return {"updated_df": df, "replacements": replacements}
