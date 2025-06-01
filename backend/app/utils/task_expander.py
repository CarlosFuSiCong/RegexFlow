# app/utils/task_expander.py

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
    Returns a list of dicts, each with:
      - "target": one of "all", "column <idx>", "row <idx>", or "cell <r>,<c>"
      - "regex"
      - "replacement"
    Raises ValueError if the target format cannot be parsed.
    """
    raw = task["target"].strip()
    regex = task["regex"]
    replacement = task["replacement"]

    # If already a normalized cell "cell R,C", just return as-is
    if re.fullmatch(r"(?i)cell\s+\d+,\d+", raw):
        return [task]

    # CASE 1: "all"
    if re.fullmatch(r"(?i)all", raw):
        return [{"target": "all", "regex": regex, "replacement": replacement}]

    # CASE 2: single cell "cell B2" or "cell AA10" (Excel-style 1-based for rows)
    if m := re.fullmatch(r"(?i)cell\s+([A-Za-z]+)(\d+)", raw):
        col_letters = m.group(1).upper()
        row_num = int(m.group(2)) - 1  # Excel-style → zero-based
        col_index = column_letter_to_index(col_letters)
        _validate_cell(df, row_num, col_index)
        return [
            {
                "target": f"cell {row_num},{col_index}",
                "regex": regex,
                "replacement": replacement,
            }
        ]

    # CASE 3: "row N" (single row, zero-based)
    if m := re.fullmatch(r"(?i)row\s+(\d+)", raw):
        row_index = int(m.group(1)) - 1
        _validate_row(df, row_index)
        return [
            {"target": f"row {row_index}", "regex": regex, "replacement": replacement}
        ]

    # CASE 4: "row N to M" (zero-based range)
    if m := re.fullmatch(r"(?i)row\s+(\d+)\s+to\s+(\d+)", raw):
        start = int(m.group(1)) - 1
        end = int(m.group(2)) - 1
        if start > end:
            start, end = end, start
        tasks = []
        for i in range(start, end + 1):
            _validate_row(df, i)
            tasks.append(
                {"target": f"row {i}", "regex": regex, "replacement": replacement}
            )
        return tasks

    # CASE 5: "row N,M,P" (comma-separated, zero-based indices)
    if m := re.fullmatch(r"(?i)row\s+(\d+(?:\s*,\s*\d+)*)", raw):
        parts = [int(x) - 1 for x in re.split(r"\s*,\s*", m.group(1))]
        tasks = []
        for i in parts:
            _validate_row(df, i)
            tasks.append(
                {"target": f"row {i}", "regex": regex, "replacement": replacement}
            )
        return tasks

    # CASE 6: "column X" (single column by letter, digit, or name)
    m6 = re.fullmatch(r"(?i)column\s+(.+)", raw)
    if m6 and ("," not in raw) and ("to" not in raw):
        col_ref = m6.group(1).strip()
        try:
            col_idx = _normalize_single_column(df, col_ref)
        except Exception as e:
            raise ValueError(f"Invalid column reference '{col_ref}': {e}")
        return [
            {"target": f"column {col_idx}", "regex": regex, "replacement": replacement}
        ]

    # CASE 7: "column X to Y" (letter or digit)
    if m := re.fullmatch(r"(?i)column\s+([A-Za-z\d]+)\s+to\s+([A-Za-z\d]+)", raw):
        first = m.group(1).strip()
        second = m.group(2).strip()
        idx1 = _normalize_single_column(df, first)
        idx2 = _normalize_single_column(df, second)
        if idx1 > idx2:
            idx1, idx2 = idx2, idx1
        return [
            {"target": f"column {i}", "regex": regex, "replacement": replacement}
            for i in range(idx1, idx2 + 1)
        ]

    # CASE 8: "column X,Y,Z" (comma-separated mix of letters, digits, or names)
    m8 = re.fullmatch(r"(?i)column\s+(.+)", raw)
    if m8 and ("," in raw):
        inner = m8.group(1)
        parts = [p.strip() for p in inner.split(",")]
        col_indexes = []
        for p in parts:
            try:
                ci = _normalize_single_column(df, p)
            except Exception as e:
                raise ValueError(f"Invalid column reference '{p}': {e}")
            col_indexes.append(ci)
        return [
            {"target": f"column {i}", "regex": regex, "replacement": replacement}
            for i in col_indexes
        ]

    # CASE 9: "row N columns C1 to C2" (zero-based)
    if m := re.fullmatch(r"(?i)row\s+(\d+)\s+columns\s+(\d+)\s+to\s+(\d+)", raw):
        row_index = int(m.group(1)) - 1
        c1 = int(m.group(2)) - 1
        c2 = int(m.group(3)) - 1
        if c1 > c2:
            c1, c2 = c2, c1
        tasks = []
        for c in range(c1, c2 + 1):
            _validate_cell(df, row_index, c)
            tasks.append(
                {
                    "target": f"cell {row_index},{c}",
                    "regex": regex,
                    "replacement": replacement,
                }
            )
        return tasks

    # CASE 10: "column X rows R1 to R2" (zero-based rows)
    if m := re.fullmatch(
        r"(?i)column\s+([A-Za-z\d]+)\s+rows\s+(\d+)\s+to\s+(\d+)", raw
    ):
        col_ref = m.group(1).strip()
        r1 = int(m.group(2)) - 1
        r2 = int(m.group(3)) - 1
        c_idx = _normalize_single_column(df, col_ref)
        if r1 > r2:
            r1, r2 = r2, r1
        tasks = []
        for r in range(r1, r2 + 1):
            _validate_cell(df, r, c_idx)
            tasks.append(
                {
                    "target": f"cell {r},{c_idx}",
                    "regex": regex,
                    "replacement": replacement,
                }
            )
        return tasks

    # CASE 11: "row N column X" (single cell by zero-based row and column reference)
    if m := re.fullmatch(r"(?i)row\s+(\d+)\s+column\s+(.+)", raw):
        row_index = int(m.group(1)) - 1
        col_ref = m.group(2).strip()
        c_idx = _normalize_single_column(df, col_ref)
        _validate_cell(df, row_index, c_idx)
        return [
            {
                "target": f"cell {row_index},{c_idx}",
                "regex": regex,
                "replacement": replacement,
            }
        ]

    # CASE 12: "range A1:C3"
    if m := re.fullmatch(r"(?i)range\s+([A-Za-z]+)(\d+):([A-Za-z]+)(\d+)", raw):
        c1_letters = m.group(1).upper()
        r1 = int(m.group(2)) - 1  # Excel-style → zero-based
        c2_letters = m.group(3).upper()
        r2 = int(m.group(4)) - 1  # Excel-style → zero-based
        c1 = column_letter_to_index(c1_letters)
        c2 = column_letter_to_index(c2_letters)
        tasks = []
        for rr in range(min(r1, r2), max(r1, r2) + 1):
            for cc in range(min(c1, c2), max(c1, c2) + 1):
                _validate_cell(df, rr, cc)
                tasks.append(
                    {
                        "target": f"cell {rr},{cc}",
                        "regex": regex,
                        "replacement": replacement,
                    }
                )
        return tasks

    # Finally, try resolving any other complex format via target_resolver
    try:
        coords = resolve_target(df, raw)
        return [
            {"target": f"cell {row},{col}", "regex": regex, "replacement": replacement}
            for row, col in coords
        ]
    except Exception as e:
        raise ValueError(f"Cannot parse target '{raw}': {e}")


def _normalize_single_column(df: pd.DataFrame, ref: str) -> int:
    """
    Helper to convert a single column reference (letter, digit, or name) to a zero-based index.
    The order of checks is:
      1) Column name (case-insensitive).
      2) Digit string → treated as zero-based index.
      3) Excel-style letters → convert via column_letter_to_index.
    """
    ref_str = ref.strip()

    # 1. Try column name (case-insensitive)
    lower_map = {col.lower(): idx for idx, col in enumerate(df.columns)}
    if ref_str.lower() in lower_map:
        return lower_map[ref_str.lower()]

    # 2. Digit string → index
    if ref_str.isdigit():
        idx = int(ref_str)
        if idx < 0 or idx >= len(df.columns):
            raise ValueError(f"Column index {idx} out of range")
        return idx

    # 3. Excel-style letters
    if re.fullmatch(r"[A-Za-z]+", ref_str):
        idx = column_letter_to_index(ref_str.upper())
        if idx < 0 or idx >= len(df.columns):
            raise ValueError(f"Column letter '{ref_str}' out of range")
        return idx

    # 4. Anything else is invalid
    raise ValueError(f"Cannot normalize column reference: '{ref}'")


def _validate_row(df: pd.DataFrame, row: int):
    """
    Ensure a row index is within DataFrame bounds.
    """
    if row < 0 or row >= len(df):
        raise ValueError(f"Row index {row} out of range (0 to {len(df)-1})")


def _validate_cell(df: pd.DataFrame, row: int, col: int):
    """
    Ensure that a (row, col) pair is within DataFrame bounds.
    """
    if row < 0 or row >= len(df):
        raise ValueError(f"Row index {row} out of range (0 to {len(df)-1})")
    if col < 0 or col >= len(df.columns):
        raise ValueError(f"Column index {col} out of range (0 to {len(df.columns)-1})")
