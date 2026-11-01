"""
Raw Data Storage

Stores raw API responses locally and optionally archives
the same JSON file in Amazon S3.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import boto3

from src.config.settings import settings
from src.ingestion.logger import get_logger

logger = get_logger(__name__)


class RawDataSaver:
    """Save raw job data locally and optionally to Amazon S3."""

    def __init__(self):
        self.base_path = settings.RAW_DATA_PATH
        self.bucket = settings.S3_RAW_BUCKET
        self.prefix = settings.S3_RAW_PREFIX.strip("/")
        self.region = settings.AWS_REGION
        self._s3_client = None

    def _get_s3_client(self):
        """Create the S3 client only when an upload is needed."""
        if self._s3_client is None:
            self._s3_client = boto3.client(
                "s3",
                region_name=self.region,
            )
        return self._s3_client

    def save(self, jobs: List[Dict]) -> Path:
        """Write a JSON file locally and optionally archive it to S3."""
        now = datetime.now()

        folder = (
            self.base_path
            / f"{now.year}"
            / f"{now.month:02}"
            / f"{now.day:02}"
        )
        folder.mkdir(parents=True, exist_ok=True)

        filename = f"jobs_{now.strftime('%Y%m%d_%H%M%S')}.json"
        filepath = folder / filename

        with filepath.open("w", encoding="utf-8") as file:
            json.dump(
                jobs,
                file,
                indent=4,
                ensure_ascii=False,
            )

        logger.info("Saved %s jobs locally to %s", len(jobs), filepath)

        if self.bucket:
            key = "/".join(
                part for part in (
                    self.prefix,
                    f"{now.year}",
                    f"{now.month:02}",
                    f"{now.day:02}",
                    filename,
                )
                if part
            )

            logger.info(
                "Uploading raw job data to s3://%s/%s",
                self.bucket,
                key,
            )

            try:
                self._get_s3_client().upload_file(
                    str(filepath),
                    self.bucket,
                    key,
                    ExtraArgs={"ContentType": "application/json"},
                )
            except Exception:
                logger.exception(
                    "S3 upload failed for local file %s",
                    filepath,
                )
                raise

            logger.info("S3 archival completed: s3://%s/%s", self.bucket, key)

        return filepath