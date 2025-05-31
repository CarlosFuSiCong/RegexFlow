# app/utils/file_parser.py

import pandas as pd
import logging

logger = logging.getLogger(__name__)


def parse_file(file):
    """
    Parses an uploaded file (.csv or .xlsx) and returns a Pandas DataFrame.

    Raises:
        ValueError: If the file format is unsupported or parsing fails.
    """
    try:
        logger.debug(f"Attempting to parse file: {file.name}")

        if file.name.endswith(".csv"):
            df = pd.read_csv(file)
        elif file.name.endswith(".xlsx"):
            df = pd.read_excel(file, engine="openpyxl")
        else:
            raise ValueError("Unsupported file format. Please upload .csv or .xlsx.")

        logger.info(
            f"File parsed successfully: {file.name}, rows: {len(df)}, columns: {list(df.columns)}"
        )
        return df

    except Exception as e:
        logger.error(f"Failed to parse file: {file.name}")
        logger.exception(e)
        raise ValueError(f"Failed to parse file: {e}")
