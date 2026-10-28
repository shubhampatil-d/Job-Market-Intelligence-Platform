"""
Job Processing Layer

Reads raw JSearch JSON files and converts them into
clean, normalized, deduplicated job records.
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

import pandas as pd

from src.config.settings import settings
from src.ingestion.logger import get_logger


logger = get_logger(__name__)


class JobProcessor:
    """
    Processes raw JSearch job data.

    Responsibilities:
    - Discover raw JSON files
    - Read raw job records
    - Normalize fields
    - Clean values
    - Handle empty API responses
    - Deduplicate jobs
    - Save processed data
    - Return processing metrics
    """

    def __init__(self):

        self.raw_path = Path(
            settings.RAW_DATA_PATH
        )

        self.processed_path = Path(
            settings.PROCESSED_DATA_PATH
        )

        self.processed_path.mkdir(
            parents=True,
            exist_ok=True,
        )

    # =========================================================
    # MAIN PIPELINE
    # =========================================================

    def run(self) -> Tuple[Path, Dict[str, int]]:

        logger.info(
            "Starting job processing"
        )

        raw_files = self._find_raw_files()

        if not raw_files:

            raise FileNotFoundError(
                f"No raw JSON files found in {self.raw_path}"
            )

        logger.info(
            "Found %d raw JSON files",
            len(raw_files),
        )

        raw_records = self._load_raw_files(
            raw_files
        )

        records_fetched = len(raw_records)

        logger.info(
            "Loaded %d raw job records",
            records_fetched,
        )

        # -----------------------------------------------------
        # Normalize
        # -----------------------------------------------------

        normalized_records = [
            self._normalize_job(job)
            for job in raw_records
        ]

        dataframe = pd.DataFrame(
            normalized_records
        )

        # -----------------------------------------------------
        # Clean
        # -----------------------------------------------------

        before_validation = len(dataframe)

        dataframe = self._clean_dataframe(
            dataframe
        )

        records_valid = len(dataframe)

        records_rejected = (
            before_validation
            - records_valid
        )

        # -----------------------------------------------------
        # Deduplicate
        # -----------------------------------------------------

        before_deduplication = len(dataframe)

        dataframe = self._deduplicate(
            dataframe
        )

        duplicates_removed = (
            before_deduplication
            - len(dataframe)
        )

        records_processed = len(dataframe)

        # -----------------------------------------------------
        # Save
        # -----------------------------------------------------

        output_path = (
            self._save_processed_data(
                dataframe
            )
        )

        metrics = {
            "records_fetched": records_fetched,
            "records_valid": records_valid,
            "records_rejected": records_rejected,
            "records_processed": records_processed,
            "records_failed": 0,
            "duplicates_removed": duplicates_removed,
        }

        logger.info(
            "Processing completed successfully. "
            "Processed %d jobs.",
            records_processed,
        )

        return output_path, metrics

    # =========================================================
    # FIND RAW FILES
    # =========================================================

    def _find_raw_files(
        self,
    ) -> List[Path]:

        return sorted(
            self.raw_path.rglob("*.json")
        )

    # =========================================================
    # LOAD RAW FILES
    # =========================================================

    def _load_raw_files(
        self,
        files: List[Path],
    ) -> List[Dict[str, Any]]:

        records = []

        for file_path in files:

            logger.info(
                "Reading raw file: %s",
                file_path,
            )

            try:

                with open(
                    file_path,
                    "r",
                    encoding="utf-8",
                ) as file:

                    data = json.load(file)

                # -------------------------------------------------
                # JSearch response
                #
                # {
                #     "jobs": [...],
                #     "cursor": ...
                # }
                # -------------------------------------------------

                if isinstance(data, dict):

                    jobs = data.get(
                        "jobs"
                    )

                    if isinstance(jobs, list):

                        if jobs:

                            records.extend(
                                jobs
                            )

                            logger.info(
                                "Loaded %d jobs from %s",
                                len(jobs),
                                file_path,
                            )

                        else:

                            logger.info(
                                "No jobs returned by %s",
                                file_path,
                            )

                        continue

                    # -------------------------------------------------
                    # Alternative API response
                    #
                    # {
                    #     "data": [...]
                    # }
                    # -------------------------------------------------

                    data_jobs = data.get(
                        "data"
                    )

                    if isinstance(
                        data_jobs,
                        list,
                    ):

                        records.extend(
                            data_jobs
                        )

                        logger.info(
                            "Loaded %d jobs from %s",
                            len(data_jobs),
                            file_path,
                        )

                        continue

                    # -------------------------------------------------
                    # Single job object
                    # -------------------------------------------------

                    if "job_id" in data:

                        records.append(
                            data
                        )

                        continue

                    logger.error(
                        "Unsupported JSON structure in %s",
                        file_path,
                    )

                # -----------------------------------------------------
                # Raw list
                # -----------------------------------------------------

                elif isinstance(
                    data,
                    list,
                ):

                    records.extend(
                        data
                    )

                    logger.info(
                        "Loaded %d jobs from %s",
                        len(data),
                        file_path,
                    )

                else:

                    logger.error(
                        "Unsupported JSON type in %s",
                        file_path,
                    )

            except json.JSONDecodeError as exc:

                logger.error(
                    "Invalid JSON file %s: %s",
                    file_path,
                    exc,
                )

            except OSError as exc:

                logger.error(
                    "Unable to read %s: %s",
                    file_path,
                    exc,
                )

        return records

    # =========================================================
    # NORMALIZE JOB
    # =========================================================

    def _normalize_job(
        self,
        job: Dict[str, Any],
    ) -> Dict[str, Any]:

        employment_types = job.get(
            "job_employment_types"
        )

        if isinstance(
            employment_types,
            list,
        ):

            employment_types = ", ".join(
                str(value).strip()
                for value in employment_types
                if value
            )

        elif employment_types is not None:

            employment_types = str(
                employment_types
            ).strip()

        apply_options = job.get(
            "apply_options"
        )

        if isinstance(
            apply_options,
            list,
        ):

            apply_options_count = len(
                apply_options
            )

        else:

            apply_options_count = 0

        job_highlights = job.get(
            "job_highlights"
        )

        if isinstance(
            job_highlights,
            dict,
        ):

            highlights = []

            for values in job_highlights.values():

                if isinstance(
                    values,
                    list,
                ):

                    for value in values:

                        highlights.append(
                            str(value).strip()
                        )

                elif values:

                    highlights.append(
                        str(values).strip()
                    )

            job_highlights = " | ".join(
                highlights
            )

        elif isinstance(
            job_highlights,
            list,
        ):

            job_highlights = " | ".join(
                str(value).strip()
                for value in job_highlights
            )

        else:

            job_highlights = None

        return {

            "job_id": self._clean_value(
                job.get("job_id")
            ),

            "job_title": self._clean_text(
                job.get("job_title")
            ),

            "employer_name": self._clean_text(
                job.get("employer_name")
            ),

            "employer_logo": self._clean_value(
                job.get("employer_logo")
            ),

            "job_publisher": self._clean_text(
                job.get("job_publisher")
            ),

            "job_employment_type":
                self._clean_value(
                    job.get(
                        "job_employment_type"
                    )
                ),

            "job_employment_types":
                employment_types,

            "job_description":
                self._clean_text(
                    job.get(
                        "job_description"
                    )
                ),

            "job_city":
                self._clean_text(
                    job.get("job_city")
                ),

            "job_state":
                self._clean_text(
                    job.get("job_state")
                ),

            "job_country":
                self._clean_text(
                    job.get("job_country")
                ),

            "job_latitude":
                job.get("job_latitude"),

            "job_longitude":
                job.get("job_longitude"),

            "job_min_salary":
                job.get("job_min_salary"),

            "job_max_salary":
                job.get("job_max_salary"),

            "job_salary_period":
                self._clean_value(
                    job.get(
                        "job_salary_period"
                    )
                ),

            "job_salary_currency":
                self._clean_value(
                    job.get(
                        "job_salary_currency"
                    )
                ),

            "job_posted_at":
                self._clean_value(
                    job.get(
                        "job_posted_at"
                    )
                ),

            "job_posted_at_datetime_utc":
                self._clean_value(
                    job.get(
                        "job_posted_at_datetime_utc"
                    )
                ),

            "job_is_remote":
                job.get(
                    "job_is_remote"
                ),

            "job_apply_is_direct":
                job.get(
                    "job_apply_is_direct"
                ),

            "job_highlights":
                job_highlights,

            "apply_options_count":
                apply_options_count,

            "job_apply_link":
                self._clean_value(
                    job.get(
                        "job_apply_link"
                    )
                ),

            "job_google_link":
                self._clean_value(
                    job.get(
                        "job_google_link"
                    )
                ),
        }

    # =========================================================
    # CLEAN DATAFRAME
    # =========================================================

    def _clean_dataframe(
        self,
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:

        if dataframe.empty:

            return dataframe

        dataframe = dataframe.dropna(
            how="all"
        )

        text_columns = [
            "job_id",
            "job_title",
            "employer_name",
            "job_city",
            "job_state",
            "job_country",
            "job_employment_type",
            "job_employment_types",
            "job_salary_period",
            "job_salary_currency",
            "job_publisher",
        ]

        for column in text_columns:

            if column in dataframe.columns:

                dataframe[column] = (
                    dataframe[column]
                    .astype("string")
                    .str.strip()
                )

        numeric_columns = [
            "job_latitude",
            "job_longitude",
            "job_min_salary",
            "job_max_salary",
            "apply_options_count",
        ]

        for column in numeric_columns:

            if column in dataframe.columns:

                dataframe[column] = pd.to_numeric(
                    dataframe[column],
                    errors="coerce",
                )

        boolean_columns = [
            "job_is_remote",
            "job_apply_is_direct",
        ]

        for column in boolean_columns:

            if column in dataframe.columns:

                dataframe[column] = (
                    dataframe[column]
                    .astype("boolean")
                )

        if (
            "job_posted_at_datetime_utc"
            in dataframe.columns
        ):

            dataframe[
                "job_posted_at_datetime_utc"
            ] = pd.to_datetime(
                dataframe[
                    "job_posted_at_datetime_utc"
                ],
                errors="coerce",
                utc=True,
            )

        # Required fields
        required_columns = [
            "job_id",
            "job_title",
            "employer_name",
        ]

        missing_columns = [
            column
            for column in required_columns
            if column not in dataframe.columns
        ]

        if missing_columns:
            raise ValueError(
                f"Missing required columns: {missing_columns}"
            )

        dataframe = dataframe.dropna(
            subset=required_columns
        )

        for column in required_columns:
            dataframe = dataframe[
                dataframe[column].astype("string").str.strip().ne("")
            ]
        return dataframe

    # =========================================================
    # DEDUPLICATE
    # =========================================================

    def _deduplicate(
        self,
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:

        if dataframe.empty:

            return dataframe

        if "job_id" in dataframe.columns:

            dataframe = dataframe.drop_duplicates(
                subset=["job_id"],
                keep="last",
            )

        else:

            dataframe = dataframe.drop_duplicates()

        return dataframe

    # =========================================================
    # SAVE PROCESSED DATA
    # =========================================================

    def _save_processed_data(
        self,
        dataframe: pd.DataFrame,
    ) -> Path:

        now = datetime.now()

        output_directory = (
            self.processed_path
            / str(now.year)
            / f"{now.month:02d}"
            / f"{now.day:02d}"
        )

        output_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        filename = (
            f"processed_jobs_"
            f"{now.strftime('%Y%m%d_%H%M%S')}.csv"
        )

        output_path = (
            output_directory
            / filename
        )

        dataframe.to_csv(
            output_path,
            index=False,
        )

        logger.info(
            "Processed data saved to %s",
            output_path,
        )

        return output_path

    # =========================================================
    # UTILITY METHODS
    # =========================================================

    @staticmethod
    def _clean_value(
        value: Any,
    ) -> Any:

        if value is None:

            return None

        if isinstance(
            value,
            str,
        ):

            value = value.strip()

            if value == "":

                return None

        return value

    @staticmethod
    def _clean_text(
        value: Any,
    ) -> Any:

        if value is None:

            return None

        value = str(value)

        value = re.sub(
            r"\s+",
            " ",
            value,
        )

        value = value.strip()

        return (
            value
            if value
            else None
        )