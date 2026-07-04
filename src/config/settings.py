"""
Application Settings

Loads all environment variables required by the project.
"""

import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()


class Settings:
    """
    Central configuration class.

    All environment variables should be accessed
    through this class.
    """

    RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")

    RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST")

    REQUEST_TIMEOUT = 30

    DEFAULT_LOCATION = "India"

    RAW_DATA_PATH = "data/raw"


settings = Settings()