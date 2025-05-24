# app/utils/openai_client.py

from openai import OpenAI
import os
import logging

logger = logging.getLogger(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def get_regex_from_nl(description: str) -> str:
    prompt = f"""You are a regex expert.
Given the following description, output ONLY the regex pattern. Do not include any explanation or quotes.

Description: {description}
Regex:"""

    try:
        logger.debug(f"Sending prompt: {description}")

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100,
            temperature=0,
        )

        regex = response.choices[0].message.content.strip()
        logger.info(f"Generated regex: {regex}")
        return regex

    except Exception as e:
        logger.exception("OpenAI call failed")
        raise ValueError("Failed to generate regex.")
