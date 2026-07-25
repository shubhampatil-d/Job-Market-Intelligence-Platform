"""
Job Ingestion Pipeline

Coordinates job fetching and raw data archival.
"""

from datetime import datetime
from typing import Dict

from src.ingestion.logger import get_logger
from src.ingestion.providers.jsearch_provider import JSearchProvider
from src.ingestion.save_raw import RawDataSaver

logger = get_logger(__name__)


class JobIngestionPipeline:
    """
    Coordinates the ingestion workflow.
    """

    def __init__(self):

        self.provider = JSearchProvider()

        self.saver = RawDataSaver()

    def run(
        self,
        keyword: str,
    ) -> Dict:

        logger.info("Starting ingestion pipeline")

        start_time = datetime.now()

        jobs = self.provider.fetch_jobs(keyword)

        file_path = self.saver.save(jobs)

        end_time = datetime.now()

        execution_time = (
            end_time - start_time
        ).total_seconds()

        metadata = {

            "keyword": keyword,

            "records": len(jobs),

            "execution_time_seconds": execution_time,

            "raw_file": str(file_path),

            "status": "SUCCESS",
        }

        logger.info(
            "Pipeline completed successfully"
        )

        return metadata