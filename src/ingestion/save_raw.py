"""
Raw Data Storage

Stores raw API responses without modification.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict

from src.config.settings import settings
from src.ingestion.logger import get_logger

logger = get_logger(__name__)


class RawDataSaver:
    """
    Saves raw job data into timestamped JSON files.
    """

    def __init__(self):

        self.base_path = settings.RAW_DATA_PATH

    def save(
        self,
        jobs: List[Dict],
    ) -> Path:

        now = datetime.now()

        folder = (
            self.base_path
            / f"{now.year}"
            / f"{now.month:02}"
            / f"{now.day:02}"
        )

        folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        filename = (
            f"jobs_{now.strftime('%Y%m%d_%H%M%S')}.json"
        )

        filepath = folder / filename

        with open(
            filepath,
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                jobs,
                file,
                indent=4,
                ensure_ascii=False,
            )

        logger.info(
            "Saved %s jobs to %s",
            len(jobs),
            filepath,
        )

        return filepath