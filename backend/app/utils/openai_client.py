# app/utils/openai_client.py

from openai import OpenAI
import os
import logging
import json
from typing import List, Dict

logger = logging.getLogger(__name__)

# Retrieve OpenAI API key from environment variables
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise EnvironmentError("OPENAI_API_KEY is not set in the environment.")

client = OpenAI(api_key=api_key)

MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


def get_regex_tasks_from_nl(description: str) -> List[Dict[str, str]]:
    """
    Parse a natural language instruction and extract regex-based editing tasks for Excel data.

    Each task includes:
    - "target": A semantic description of the region to edit (e.g., "row 2", "column Email", "first 3 columns of row 1").
                Use a helper like `resolve_target()` to convert it into exact DataFrame locations.
    - "regex": A raw regex pattern to match.
    - "replacement": The string to replace matches with (can be empty).

    Args:
        description (str): English instruction with one or more edit requests.

    Returns:
        List[Dict[str, str]]: A list of edit tasks.

    Example:
    [
        {
            "target": "column Contact",
            "regex": "\\b\\d{3}[-.]?\\d{3}[-.]?\\d{4}\\b",
            "replacement": "[hidden]"
        },
        {
            "target": "first 2 rows of column Email",
            "regex": "\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}\\b",
            "replacement": "[redacted]"
        }
    ]
    """
    # Construct a prompt to request a JSON array of edits
    prompt = f"""
You are a smart assistant.

Your task is to extract regex-based edit instructions from the following Excel-related description.

Assume the data is from an Australian dataset. Here are some useful patterns to keep in mind:

- Phone numbers may start with "+61", "04", or "614", and appear in various formats such as:
  - "+61 412 345 678"
  - "+61412345678"
  - "0412345678"
  - "+61-412-345-678"
  - "04 12 345 678"
These should be matched by a single regex if the description requests replacing phone numbers.

- Dates may follow "DD/MM/YYYY" or "YYYY-MM-DD" format  
- Postal codes are 4-digit numbers (e.g., 2000, 3004)  
- Email addresses follow the standard pattern: user@domain.com  
- ABNs (Australian Business Numbers) are 11-digit numbers, optionally formatted with spaces (e.g., "12 345 678 901")

---

For each described edit, output a JSON object with:
- `target`: where to apply the edit. It must be one of:
    - "all"
    - "row <number>"
    - "column <name>"
    - "cell <Excel-style>"
    - "row <number> columns <start> to <end>"
    - "column <name> rows <start> to <end>"
    - "range <A1>:<C3>"
    - "row even" → a list of even-numbered rows
    - "column odd" → a list of odd-numbered columns
    - "cell range A1, B2, C3" → a list of specified cells

Support common phrases such as:
- "first 3 columns of row 2" → "row 2 columns 0 to 2"
- "first 2 rows of column Email" → "column Email rows 0 to 1"
- "first 4 rows" → ["row 0", "row 1", "row 2", "row 3"]

---

Regex patterns must:
- Be written as raw regex (no explanation or quotes)
- Use **double-escaped** syntax (e.g., `\\d{4}` should be written as `\\\\d{4}`)
- Focus only on matching the **described elements**
- Be case-sensitive only when required

Replacements can be plain strings, e.g., `[redacted]`, `""`, or a specific value.

Only return a **raw JSON array**. Do not include Markdown, comments, or explanation.

---

Description: {description}  
JSON:

"""

    try:
        logger.debug(f"Sending prompt: {description}")

        # Send prompt to OpenAI API
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,  # Allow enough room for multiple edits
            temperature=0,  # Deterministic output
        )

        content = response.choices[0].message.content.strip()
        logger.info(f"Parsed tasks: {content}")

        return json.loads(content)

    except Exception as e:
        logger.exception("Failed to parse multiple instructions")
        raise ValueError(
            "Could not interpret the description into multiple edit tasks."
        )
