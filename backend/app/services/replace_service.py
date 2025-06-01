# app/services/replace_service.py

import pandas as pd
import logging
from typing import List, Dict
from app.utils.replace_all_matches import replace_all_matches
from app.utils.replace_column_matches import replace_column_matches
from app.utils.replace_row_matches import replace_row_matches
from app.utils.replace_cell_match import replace_cell_match

logger = logging.getLogger(__name__)


def apply_tasks(df: pd.DataFrame, tasks: List[Dict[str, str]]) -> List[Dict]:
    """
    Apply a list of regex tasks to the given DataFrame.

    Each task should contain:
        - target: e.g., "column Email", "row 2", "cell B2", or "all"
        - regex: the pattern to match
        - replacement: the replacement string

    Returns a list of all successful replacements.
    Tasks with invalid format or failed replacements will be skipped with a warning.
    """
    all_replacements = []

    for task in tasks:
        try:
            target = task["target"]
            pattern = task["regex"]
            replacement = task["replacement"]

            # Normalize ".*" to "^.*$" to avoid duplicate replacements
            if pattern.strip() == ".*":
                logger.debug(f"Normalizing regex '.*' to '^.*$' for task: {task}")
                pattern = "^.*$"

            if target.startswith("column "):
                col = target.replace("column ", "")
                all_replacements += replace_in_column(df, col, pattern, replacement)

            elif target.startswith("row "):
                row_idx = int(target.replace("row ", ""))
                all_replacements += replace_in_row(df, row_idx, pattern, replacement)

            elif target.startswith("cell "):
                cell = target.replace("cell ", "").upper()
                col_letter = "".join(filter(str.isalpha, cell))
                row_number = int("".join(filter(str.isdigit, cell))) - 1
                all_replacements += replace_in_cell(
                    df, row_number, col_letter, pattern, replacement
                )

            elif target == "all":
                all_replacements += replace_in_all(df, pattern, replacement)

            else:
                raise ValueError(f"Unsupported target type: '{target}'")

        except Exception as e:
            logger.warning(f"Skipping task due to error: {task} → {e}")

    logger.info(f"Total replacements applied: {len(all_replacements)}")
    return all_replacements


def replace_in_all(df: pd.DataFrame, pattern: str, replacement: str) -> List[Dict]:
    """
    Replace regex matches across the entire DataFrame.
    """
    try:
        logger.info(f"Applying regex to entire table: pattern='{pattern}'")
        result = replace_all_matches(df, pattern, replacement, inplace=True)
        return result["replacements"]
    except Exception as e:
        logger.exception("Failed to apply replacement to entire table.")
        raise ValueError(f"Regex replacement failed (all): {e}")


def replace_in_column(
    df: pd.DataFrame, col_name: str, pattern: str, replacement: str
) -> List[Dict]:
    """
    Replace regex matches in a specific column.
    Supports both column name and numeric index (as string or int).
    """
    try:
        # Normalize input
        if isinstance(col_name, int) or (
            isinstance(col_name, str) and col_name.strip().isdigit()
        ):
            col_index = int(col_name)
            if col_index < 0 or col_index >= len(df.columns):
                raise ValueError(f"Column index {col_index} is out of range.")
            col_name = df.columns[col_index]
        else:
            col_name = col_name.strip()

        logger.info(f"Applying regex to column '{col_name}': pattern='{pattern}'")

        result = replace_column_matches(
            df, col_name, pattern, replacement, inplace=True
        )
        return result["replacements"]

    except Exception as e:
        logger.exception(f"Failed to apply replacement to column '{col_name}'.")
        raise ValueError(f"Regex replacement failed (column={col_name}): {e}")


def replace_in_row(
    df: pd.DataFrame, row_index: int, pattern: str, replacement: str
) -> List[Dict]:
    """
    Replace regex matches in a specific row.
    """
    try:
        logger.info(f"Applying regex to row {row_index}: pattern='{pattern}'")
        result = replace_row_matches(df, row_index, pattern, replacement, inplace=True)
        return result["replacements"]
    except Exception as e:
        logger.exception(f"Failed to apply replacement to row {row_index}.")
        raise ValueError(f"Regex replacement failed (row={row_index}): {e}")


def replace_in_cell(
    df: pd.DataFrame, row_index: int, col_name: str, pattern: str, replacement: str
) -> List[Dict]:
    """
    Replace regex match in a specific cell.
    """
    try:
        logger.info(
            f"Applying regex to cell ({row_index}, '{col_name}'): pattern='{pattern}'"
        )
        result = replace_cell_match(
            df, f"{col_name}{row_index + 1}", pattern, replacement, inplace=True
        )
        return result["replacements"]
    except Exception as e:
        logger.exception(
            f"Failed to apply replacement to cell ({row_index}, '{col_name}')."
        )
        raise ValueError(
            f"Regex replacement failed (cell={col_name}{row_index + 1}): {e}"
        )


def preview_tasks(df: pd.DataFrame, tasks: List[Dict[str, str]]) -> List[Dict]:
    from copy import deepcopy

    original_df = deepcopy(df)
    preview_df = deepcopy(df)

    apply_tasks(preview_df, tasks)

    diffs = []
    for i in range(len(original_df)):
        for col in original_df.columns:
            before = original_df.at[i, col]
            after = preview_df.at[i, col]
            if pd.notnull(before) and pd.notnull(after) and str(before) != str(after):
                diffs.append(
                    {
                        "row": i + 1,
                        "column": col,
                        "original": str(before),
                        "modified": str(after),
                    }
                )

    logger.info(f"Preview generated with {len(diffs)} changes.")
    return diffs
