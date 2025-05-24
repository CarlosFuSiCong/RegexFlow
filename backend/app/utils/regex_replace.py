# app/utils/regex_replace.py

import pandas as pd
import re
import logging
from typing import List, Dict, Union

logger = logging.getLogger(__name__)


def replace_all_matches_in_table(
    df: pd.DataFrame, pattern: str, replacement: str, inplace: bool = False
) -> Dict[str, Union[pd.DataFrame, List[Dict]]]:

    try:
        regex = re.compile(pattern)
    except re.error as e:
        logger.error(f"Invalid regex pattern: {e}")
        raise ValueError(f"Invalid regex pattern: {e}")

    if not inplace:
        df = df.copy()

    replacements = []
    try:
        for row_idx in range(len(df)):
            for col in df.columns:
                original = str(df.at[row_idx, col])
                new_val = regex.sub(replacement, original)
                if new_val != original:
                    df.at[row_idx, col] = new_val
                    replacements.append(
                        {"row": row_idx, "column": col, "from": original, "to": new_val}
                    )
    except Exception as e:
        logger.exception("Error occurred during regex replacement.")
        raise RuntimeError("Error occurred during replacement process.") from e

    if not replacements:
        logger.info("No matches found for replacement.")
        raise ValueError("No matches found in entire table.")

    logger.info(f"Total replacements made: {len(replacements)}")
    return {"updated_df": df, "replacements": replacements}
