"""
Pipeline Monitoring

Provides structured metrics for pipeline executions.

The monitoring layer tracks:

- execution status
- records fetched
- records processed
- records rejected
- duplicate records
- execution time
- output location
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from src.ingestion.logger import get_logger


logger = get_logger(__name__)


class PipelineMonitor:
    """
    Collects and stores pipeline execution metrics.
    """

    def __init__(
        self,
        metrics_directory: str = "data/monitoring",
    ):
        self.metrics_directory = Path(
            metrics_directory
        )

        self.metrics_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

    # ---------------------------------------------------------
    # Create metrics
    # ---------------------------------------------------------

    def create_run(
        self,
        pipeline_name: str,
    ) -> Dict[str, Any]:
        """
        Create a new pipeline run.
        """

        run_id = datetime.now().strftime(
            "%Y%m%d_%H%M%S_%f"
        )

        return {
            "run_id": run_id,
            "pipeline_name": pipeline_name,
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "status": "RUNNING",
            "records_fetched": 0,
            "records_valid": 0,
            "records_rejected": 0,
            "records_processed": 0,
            "records_failed": 0,
            "duplicates_removed": 0,
            "execution_time_seconds": None,
            "output_path": None,
            "error": None,
        }

    # ---------------------------------------------------------
    # Complete run
    # ---------------------------------------------------------

    def complete_run(
        self,
        metrics: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Mark a pipeline run as successful.
        """

        end_time = datetime.now()

        start_time = datetime.fromisoformat(
            metrics["start_time"]
        )

        metrics["end_time"] = (
            end_time.isoformat()
        )

        metrics["execution_time_seconds"] = (
            end_time - start_time
        ).total_seconds()

        metrics["status"] = "SUCCESS"

        self._save_metrics(metrics)

        logger.info(
            "Pipeline monitoring recorded SUCCESS "
            "for run %s",
            metrics["run_id"],
        )

        return metrics

    # ---------------------------------------------------------
    # Fail run
    # ---------------------------------------------------------

    def fail_run(
        self,
        metrics: Dict[str, Any],
        error: Exception,
    ) -> Dict[str, Any]:
        """
        Mark a pipeline run as failed.
        """

        end_time = datetime.now()

        start_time = datetime.fromisoformat(
            metrics["start_time"]
        )

        metrics["end_time"] = (
            end_time.isoformat()
        )

        metrics["execution_time_seconds"] = (
            end_time - start_time
        ).total_seconds()

        metrics["status"] = "FAILED"

        metrics["error"] = str(error)

        self._save_metrics(metrics)

        logger.error(
            "Pipeline monitoring recorded FAILURE "
            "for run %s: %s",
            metrics["run_id"],
            error,
        )

        return metrics

    # ---------------------------------------------------------
    # Update metrics
    # ---------------------------------------------------------

    @staticmethod
    def update_metrics(
        metrics: Dict[str, Any],
        *,
        records_fetched: Optional[int] = None,
        records_valid: Optional[int] = None,
        records_rejected: Optional[int] = None,
        records_processed: Optional[int] = None,
        records_failed: Optional[int] = None,
        duplicates_removed: Optional[int] = None,
        output_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Update pipeline metrics.
        """

        if records_fetched is not None:
            metrics[
                "records_fetched"
            ] = records_fetched

        if records_valid is not None:
            metrics[
                "records_valid"
            ] = records_valid

        if records_rejected is not None:
            metrics[
                "records_rejected"
            ] = records_rejected

        if records_processed is not None:
            metrics[
                "records_processed"
            ] = records_processed

        if records_failed is not None:
            metrics[
                "records_failed"
            ] = records_failed

        if duplicates_removed is not None:
            metrics[
                "duplicates_removed"
            ] = duplicates_removed

        if output_path is not None:
            metrics[
                "output_path"
            ] = output_path

        return metrics

    # ---------------------------------------------------------
    # Save metrics
    # ---------------------------------------------------------

    def _save_metrics(
        self,
        metrics: Dict[str, Any],
    ) -> Path:
        """
        Save pipeline metrics as JSON.
        """

        run_id = metrics["run_id"]

        output_path = (
            self.metrics_directory
            / f"pipeline_run_{run_id}.json"
        )

        with open(
            output_path,
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                metrics,
                file,
                indent=4,
                default=str,
            )

        return output_path