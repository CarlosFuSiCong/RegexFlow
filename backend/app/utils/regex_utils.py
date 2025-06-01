# app/utils/regex_utils.py

import re


def convert_dollar_groups_to_python(replacement: str) -> str:
    """
    Convert $1, $2, ... to \g<1>, \g<2> for Python's re.sub.
    """
    return re.sub(r"\$(\d+)", r"\\g<\1>", replacement)
