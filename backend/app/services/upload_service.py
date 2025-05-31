# app/services/upload_service.py

import logging
from app.utils.file_parser import parse_file

logger = logging.getLogger(__name__)  # Get module-level logger


def handle_upload(file):
    """
    Parses the uploaded file and returns the full DataFrame and column names.
    """
    try:
        logger.debug(f"Received file for upload: {file.name}")
        df = parse_file(file)
        columns = list(df.columns)
        logger.info(f"File parsed successfully: {file.name}, columns: {columns}")
        return df, columns
    except Exception as e:
        logger.error(f"Failed to process uploaded file: {file.name}")
        logger.exception(e)  # logs full traceback
        raise ValueError(f"Upload failed: {e}")
