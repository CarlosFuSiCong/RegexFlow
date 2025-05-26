from typing import List, Dict
import pandas as pd
import re
import logging
from app.utils.target_resolver import resolve_target, column_letter_to_index
from app.utils.normalize_column_reference import normalize_column_reference

logger = logging.getLogger(__name__)


def expand_task(df: pd.DataFrame, task: Dict[str, str]) -> List[Dict[str, str]]:
    """
    Expand a task into finer-grained tasks (row, column, or cell) depending on the target format.
    - Always returns one or more normalized task dicts.
    - All 'column' references are normalized to index-based form: "column <number>"
    """
    target = task["target"].strip().lower()
    regex = task["regex"]
    replacement = task["replacement"]

    # --- CASE 1: keep as-is ---
    if (
        target == "all"
        or target.startswith("cell ")
        or (
            target.startswith("row ")
            and "to" not in target
            and "," not in target
            and "columns" not in target
        )
        or (
            target.startswith("column ")
            and "to" not in target
            and "," not in target
            and "rows" not in target
        )
    ):
        return [task]

    # --- CASE 2: row N to M ---
    if m := re.fullmatch(r"row (\d+) to (\d+)", target):
        start, end = int(m.group(1)), int(m.group(2))
        return [
            {"target": f"row {i}", "regex": regex, "replacement": replacement}
            for i in range(start, end + 1)
        ]

    # --- CASE 3: row N,M,P ---
    if m := re.fullmatch(r"row ((\d+,?)+)", target):
        row_indices = [int(x) for x in m.group(1).replace(" ", "").split(",")]
        return [
            {"target": f"row {i}", "regex": regex, "replacement": replacement}
            for i in row_indices
        ]

    # --- CASE 4: column A to D ---
    if m := re.fullmatch(r"column ([a-z]+) to ([a-z]+)", target):
        i1 = column_letter_to_index(m.group(1))
        i2 = column_letter_to_index(m.group(2))
        return [
            {"target": f"column {i}", "regex": regex, "replacement": replacement}
            for i in range(i1, i2 + 1)
        ]

    # --- CASE 5: column 1 to 4 ---
    if m := re.fullmatch(r"column (\d+) to (\d+)", target):
        i1, i2 = int(m.group(1)), int(m.group(2))
        return [
            {"target": f"column {i}", "regex": regex, "replacement": replacement}
            for i in range(i1, i2 + 1)
        ]

    # --- CASE 6: column A,C,E or column 0,2,4 or column Email,Score ---
    if m := re.fullmatch(r"column (([^,]+,?)+)", target):
        refs = m.group(1).replace(" ", "").split(",")
        try:
            col_indexes = [normalize_column_reference(df, r) for r in refs]
        except Exception as e:
            logger.warning(f"Invalid column refs: {refs}")
            return [task]
        return [
            {"target": f"column {i}", "regex": regex, "replacement": replacement}
            for i in col_indexes
        ]

    # --- CASE 7: complex case (row + column), delegate to resolve_target ---
    try:
        coords = resolve_target(df, target)
        return [
            {
                "target": f"cell {row},{col}",
                "regex": regex,
                "replacement": replacement,
            }
            for row, col in coords
        ]
    except Exception as e:
        logger.warning(f"Failed to expand complex target '{target}': {e}")
        return [task]
