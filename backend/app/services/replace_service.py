# app/services/replace_service.py

import json
import pandas as pd
import logging
from app.utils.regex_replace import replace_all_matches_in_table

logger = logging.getLogger(__name__)


def handle_full_table_replacement(session, pattern: str, replacement: str):
    try:
        if "uploaded_data" not in session:
            raise ValueError(
                "No uploaded data found in session. Please upload a file first."
            )

        json_data = session["uploaded_data"]
        df = pd.read_json(json_data)

        result = replace_all_matches_in_table(df, pattern, replacement, inplace=False)
        preview = result["replacements"][:10]

        session["uploaded_data"] = result["updated_df"].to_json()

        logger.info(f"Regex applied to entire table with pattern '{pattern}'")
        return {"replacements": preview}

    except Exception as e:
        logger.exception("Regex full-table replacement failed")
        raise ValueError(f"Full-table replacement failed: {e}")
