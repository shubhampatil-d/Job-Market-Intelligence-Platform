"""
Job Ingestion Pipeline

Coordinates job fetching and raw data archival.
"""

from datetime import datetime
from typing import Dict

from src.ingestion.logger import get_logger
from src.ingestion.providers.jsearch_provider import JSearchProvider
from src.ingestion.save_raw import RawDataSaver
from src.validation.validator import JobValidator
from pathlib import Path

logger = get_logger(__name__)


class JobIngestionPipeline:
    """
    Coordinates the ingestion workflow.
    """

    def __init__(self):

        self.provider = JSearchProvider()
        self.validator= JobValidator()
        self.saver = RawDataSaver()
        


    def run(
        self,
        keyword: str,
    ) -> Dict:

        logger.info("Starting ingestion pipeline")

        start_time = datetime.now()

        jobs = self._fetch_jobs(keyword)

        valid_jobs = self._validate_jobs(jobs)

        file_path = self._archive_jobs(valid_jobs)

        execution_time = (
        datetime.now() - start_time
        ).total_seconds()

        metadata = self._build_metadata(
            keyword=keyword,
            jobs=jobs,
            valid_jobs=valid_jobs,
            file_path=file_path,
            execution_time=execution_time,
        )

        logger.info("Pipeline completed successfully")

        return metadata

    def _fetch_jobs(
        self,
        keyword: str,
    ) -> list[dict]:

        logger.info("Fetching jobs from provider")

        return self.provider.fetch_jobs(keyword)

    def _validate_jobs(
            self,
            jobs: list[dict],
    ) -> list[dict]: 
        
        logger.info("Validating jobs")

        return self.validator.validate(jobs)

    def _archive_jobs(
            self,
            jobs: list[dict],
    ) -> Path:
        
        logger.info("Saving raw jobs")

        return self.saver.save(jobs)

    def _build_metadata(
            self,
            keyword: str,
            jobs: list[dict],
            valid_jobs: list[dict],
            file_path: Path,
            execution_time: float,
    ) -> dict:
        return {
            "keyword": keyword,
            "records": len(valid_jobs),
            "invalid_records":len(jobs)-len(valid_jobs),
            "execution_time_seconds": execution_time,
            "raw_file": str(file_path),
            "status": "SUCCESS",
        }