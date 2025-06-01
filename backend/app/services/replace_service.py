# app/services/replace_service.py

import pandas as pd
import logging
from typing import List, Dict

from app.utils.replace_all_matches import replace_all_matches
from app.utils.replace_column_matches import replace_column_matches
from app.utils.replace_row_matches import replace_row_matches
from app.utils.replace_cell_match import replace_cell_match

# Notice: use the utils path for task_expander, since that's where it lives
from app.utils.task_expander import expand_task

logger = logging.getLogger(__name__)


def apply_tasks(df: pd.DataFrame, tasks: List[Dict[str, str]]) -> List[Dict]:
    """
    Apply a list of regex tasks to the given DataFrame.

    1. First, expand each high-level task into simple tasks (cell/row/column/all).
    2. Run the appropriate replace function for each simple task.
    3. Return all replacement records.
    """
    all_replacements = []

    for task in tasks:
        # Expand higher-level task (e.g., "column Email rows 0 to 2") into simple tasks
        try:
            expanded = expand_task(df, task)
        except Exception as e:
            logger.warning(f"Failed to expand task {task}: {e}")
            continue

        # Process each simple task from the expansion
        for small_task in expanded:
            try:
                tgt = small_task[
                    "target"
                ]  # e.g., "cell 0,1" or "row 2" or "column 3" or "all"
                pattern = small_task["regex"]
                replacement = small_task["replacement"]

                # Normalize ".*" to "^.*$" to ensure full-string match if needed
                if pattern.strip() == ".*":
                    logger.debug(
                        f"Normalizing regex '.*' to '^.*$' for task: {small_task}"
                    )
                    pattern = "^.*$"

                # Four types of simple targets:
                # 1) "all" => entire DataFrame
                # 2) "column N" => column by index or name
                # 3) "row N" => single row by zero-based index
                # 4) "cell R,C" => single cell by row R and column C (both zero-based)
                if tgt.lower() == "all":
                    all_replacements += replace_in_all(df, pattern, replacement)

                elif tgt.lower().startswith("column "):
                    col_spec = tgt[len("column ") :].strip()
                    all_replacements += replace_in_column(
                        df, col_spec, pattern, replacement
                    )

                elif tgt.lower().startswith("row "):
                    row_idx = int(tgt[len("row ") :].strip())
                    all_replacements += replace_in_row(
                        df, row_idx, pattern, replacement
                    )

                elif tgt.lower().startswith("cell "):
                    coords = tgt[len("cell ") :].split(",")
                    row_idx = int(coords[0].strip())
                    col_idx = int(coords[1].strip())
                    all_replacements += replace_in_cell(
                        df, row_idx, col_idx, pattern, replacement
                    )

                else:
                    # This should not happen if expand_task returns valid targets
                    raise ValueError(f"Unsupported normalized target: '{tgt}'")

            except Exception as e:
                logger.warning(f"Skipping small task due to error: {small_task} → {e}")

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
    df: pd.DataFrame, col_name: str | int, pattern: str, replacement: str
) -> List[Dict]:
    """
    Replace regex matches in a specific column.

    col_name: int or digit string => zero-based column index
              otherwise => column name (must exist in df.columns)
    """
    try:
        # If col_name is numeric (as int or digit string), treat as index
        if isinstance(col_name, int) or (
            isinstance(col_name, str) and col_name.strip().isdigit()
        ):
            col_index = int(col_name)
            if col_index < 0 or col_index >= len(df.columns):
                raise ValueError(f"Column index {col_index} is out of range.")
            col_name_real = df.columns[col_index]
        else:
            col_name_real = col_name.strip()
            if col_name_real not in df.columns:
                raise ValueError(
                    f"Column '{col_name_real}' does not exist in DataFrame."
                )

        logger.info(f"Applying regex to column '{col_name_real}': pattern='{pattern}'")
        result = replace_column_matches(
            df, col_name_real, pattern, replacement, inplace=True
        )
        return result["replacements"]

    except Exception as e:
        logger.exception(f"Failed to apply replacement to column '{col_name}'.")
        raise ValueError(f"Regex replacement failed (column={col_name}): {e}")


def replace_in_row(
    df: pd.DataFrame, row_index: int, pattern: str, replacement: str
) -> List[Dict]:
    """
    Replace regex matches in all cells of a specific row (zero-based index).
    """
    try:
        if row_index < 0 or row_index >= len(df):
            raise ValueError(f"Row index {row_index} is out of range.")
        logger.info(f"Applying regex to row {row_index}: pattern='{pattern}'")
        result = replace_row_matches(df, row_index, pattern, replacement, inplace=True)
        return result["replacements"]
    except Exception as e:
        logger.exception(f"Failed to apply replacement to row {row_index}.")
        raise ValueError(f"Regex replacement failed (row={row_index}): {e}")


def replace_in_cell(
    df: pd.DataFrame, row_index: int, col_index: int, pattern: str, replacement: str
) -> List[Dict]:
    """
    Replace regex match in a single cell, specified by zero-based (row_index, col_index).
    """
    try:
        if row_index < 0 or row_index >= len(df):
            raise ValueError(f"Row index {row_index} is out of range.")
        if col_index < 0 or col_index >= len(df.columns):
            raise ValueError(f"Column index {col_index} is out of range.")

        # Convert column index to Excel-style letter, e.g., 0 -> "A", 1 -> "B"
        col_letter = _column_index_to_letter(col_index)
        # Build the cell reference string, e.g., "B2" for row_index=1, col_index=1
        cell_ref = f"{col_letter}{row_index + 1}"

        logger.info(
            f"Applying regex to cell ({row_index}, {col_index}) -> '{cell_ref}': pattern='{pattern}'"
        )
        result = replace_cell_match(df, cell_ref, pattern, replacement, inplace=True)
        return result["replacements"]

    except Exception as e:
        logger.exception(
            f"Failed to apply replacement to cell (row={row_index}, col={col_index})."
        )
        letter = _column_index_to_letter(col_index)
        raise ValueError(
            f"Regex replacement failed (cell={letter}{row_index + 1}): {e}"
        )


def preview_tasks(df: pd.DataFrame, tasks: List[Dict[str, str]]) -> List[Dict]:
    """
    Generate a preview of changes without modifying the original DataFrame.
    """
    from copy import deepcopy

    original_df = deepcopy(df)
    preview_df = deepcopy(df)

    apply_tasks(preview_df, tasks)

    diffs = []
    for i in range(len(original_df)):
        for col in original_df.columns:
            before = original_df.at[i, col]
            after = preview_df.at[i, col]
            # Record only when both values are non-null and differ as strings
            if pd.notnull(before) and pd.notnull(after) and str(before) != str(after):
                diffs.append(
                    {
                        "row": i + 1,  # use 1-based row number in output
                        "column": col,
                        "original": str(before),
                        "modified": str(after),
                    }
                )

    logger.info(f"Preview generated with {len(diffs)} changes.")
    return diffs


def _column_index_to_letter(col_idx: int) -> str:
    """
    Convert a 0-based column index to an Excel-style column letter.
    Examples:
      0 -> "A", 1 -> "B", 25 -> "Z", 26 -> "AA"
    """
    letters = ""
    n = col_idx + 1
    while n > 0:
        n, remainder = divmod(n - 1, 26)
        letters = chr(65 + remainder) + letters
    return letters
