"""
Application Settings

Loads all environment variables required by the project.
"""

import os
from dotenv import load_dotenv
from pathlib import Path

# Project root
BASE_DIR = Path(__file__).resolve().parents[2]

# Load environment variables
load_dotenv(BASE_DIR / ".env")

class Settings:
    """
    Central configuration class.

    All environment variables should be accessed
    through this class.
    """

    RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")

    RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST")

    REQUEST_TIMEOUT = 30

    MAX_RETRIES = 3

    DEFAULT_LOCATION = "India"

    RAW_DATA_PATH = BASE_DIR / "data" / "raw"

    PROCESSED_DATA_PATH = BASE_DIR / "data" / "processed"

    ARCHIVE_DATA_PATH = BASE_DIR / "data" / "archive"



settings = Settings()