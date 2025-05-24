# app/services/download_service.py

import pandas as pd
import logging
from io import StringIO, BytesIO

logger = logging.getLogger(__name__)


def get_file_from_session(session) -> tuple[bytes, str, str]:
    if "uploaded_data" not in session:
        raise ValueError(
            "No processed data found in session. Please upload and process a file first."
        )

    try:
        format = session.get("uploaded_format", "csv").lower()
        df = pd.read_json(session["uploaded_data"])

        if format == "xlsx":
            buffer = BytesIO()
            df.to_excel(buffer, index=False, engine="openpyxl")
            buffer.seek(0)
            logger.info("XLSX file generated for download")
            return (
                buffer.read(),
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "processed_data.xlsx",
            )

        else:
            csv_buffer = StringIO()
            df.to_csv(csv_buffer, index=False)
            logger.info("CSV file generated for download")
            return (
                csv_buffer.getvalue().encode("utf-8"),
                "text/csv",
                "processed_data.csv",
            )

    except Exception as e:
        logger.exception("Failed to generate file from session data")
        raise ValueError("Failed to prepare data for download.")
