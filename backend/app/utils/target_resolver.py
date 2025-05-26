import re
import pandas as pd
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)


def resolve_target(df: pd.DataFrame, target: str) -> List[Tuple[int, int]]:
    """
    Convert semantic target into list of (row, col) coordinates.
    Supports:
    - "row 3"
    - "column Email"
    - "cell 1,2"
    - "column Email rows 1 to 2"
    - "row 1 columns 0 to 2"
    - "range A1:C3"
    """
    target = target.strip().lower()

    if m := re.fullmatch(r"row (\d+)", target):
        row = int(m.group(1))
        return [(row, c) for c in range(len(df.columns))]

    if m := re.fullmatch(r"column (.+)", target):
        col = m.group(1).strip()
        if col not in df.columns:
            raise ValueError(f"Column '{col}' not found.")
        col_index = df.columns.get_loc(col)
        return [(r, col_index) for r in range(len(df))]

    if m := re.fullmatch(r"cell (\d+),(\d+)", target):
        return [(int(m.group(1)), int(m.group(2)))]

    if m := re.fullmatch(r"column (.+) rows (\d+) to (\d+)", target):
        col = m.group(1).strip()
        r1, r2 = int(m.group(2)), int(m.group(3))
        if col not in df.columns:
            raise ValueError(f"Column '{col}' not found.")
        col_index = df.columns.get_loc(col)
        return [(r, col_index) for r in range(r1, r2 + 1)]

    if m := re.fullmatch(r"row (\d+) columns (\d+) to (\d+)", target):
        row = int(m.group(1))
        c1, c2 = int(m.group(2)), int(m.group(3))
        return [(row, c) for c in range(c1, c2 + 1)]

    if m := re.fullmatch(r"range ([a-z]+)(\d+):([a-z]+)(\d+)", target):
        c1, r1, c2, r2 = m.groups()
        r1, r2 = int(r1) - 1, int(r2) - 1
        col_start = column_letter_to_index(c1.upper())
        col_end = column_letter_to_index(c2.upper())
        return [
            (r, c) for r in range(r1, r2 + 1) for c in range(col_start, col_end + 1)
        ]

    raise ValueError(f"Unrecognized target format: '{target}'")


def column_letter_to_index(col: str) -> int:
    index = 0
    for char in col:
        index = index * 26 + (ord(char.upper()) - ord("A") + 1)
    return index - 1
