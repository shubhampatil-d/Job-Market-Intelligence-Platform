import json
import logging
from pathlib import Path

import pandas as pd

from src.warehouse.database import get_engine, get_session
from src.warehouse.models import Job, Base

logger = logging.getLogger(__name__)


class JobWarehouseLoader:

    def __init__(self):
        self.engine = get_engine()

    def initialize_database(self):
        Base.metadata.create_all(self.engine)
        logger.info("Warehouse tables initialized successfully.")

    def load_csv(self, csv_path: str | Path):
        csv_path = Path(csv_path)

        if not csv_path.exists():
            raise FileNotFoundError(
                f"Processed CSV not found: {csv_path}"
            )

        logger.info(f"Loading processed data from {csv_path}")

        df = pd.read_csv(csv_path)

        if df.empty:
            logger.warning("CSV contains no records.")

            return {
                "records_read": 0,
                "records_inserted": 0,
                "records_updated": 0,
                "records_skipped": 0,
            }

        session = get_session()

        inserted = 0
        updated = 0
        skipped = 0

        try:
            # Get all job IDs from this batch
            job_ids = [
                job_id
                for job_id in df["job_id"].dropna().tolist()
                if job_id
            ]

            # SQLAlchemy 1.4-compatible query
            existing_jobs = (
                session.query(Job)
                .filter(Job.job_id.in_(job_ids))
                .all()
            )

            existing_jobs_map = {
                job.job_id: job
                for job in existing_jobs
            }

            for record in df.to_dict(orient="records"):

                job_id = self._clean_value(
                    record.get("job_id")
                )

                if not job_id:
                    skipped += 1
                    continue

                payload = self._build_payload(record)

                existing_job = existing_jobs_map.get(job_id)

                # --------------------------------------------------
                # NEW JOB → INSERT
                # --------------------------------------------------
                if existing_job is None:

                    job = Job(**payload)

                    session.add(job)

                    existing_jobs_map[job_id] = job

                    inserted += 1

                # --------------------------------------------------
                # EXISTING JOB → CHECK FOR CHANGES
                # --------------------------------------------------
                else:

                    changed = False

                    for field, new_value in payload.items():

                        if field == "job_id":
                            continue

                        old_value = getattr(
                            existing_job,
                            field,
                        )

                        if not self._values_equal(
                            old_value,
                            new_value,
                        ):
                            setattr(
                                existing_job,
                                field,
                                new_value,
                            )

                            changed = True

                    if changed:
                        updated += 1
                    else:
                        skipped += 1

            # Commit entire batch
            session.commit()

            logger.info(
                "Warehouse load completed successfully. "
                f"Inserted={inserted}, "
                f"Updated={updated}, "
                f"Skipped={skipped}"
            )

            return {
                "records_read": len(df),
                "records_inserted": inserted,
                "records_updated": updated,
                "records_skipped": skipped,
            }

        except Exception:

            session.rollback()

            logger.exception(
                "Warehouse load failed. "
                "Transaction rolled back."
            )

            raise

        finally:
            session.close()

    # --------------------------------------------------------------
    # BUILD DATABASE RECORD
    # --------------------------------------------------------------

    def _build_payload(self, record):

        return {
            "job_id": self._clean_value(
                record.get("job_id")
            ),

            "job_title": self._clean_value(
                record.get("job_title")
            ),

            "employer_name": self._clean_value(
                record.get("employer_name")
            ),

            "employer_logo": self._clean_value(
                record.get("employer_logo")
            ),

            "job_publisher": self._clean_value(
                record.get("job_publisher")
            ),

            "job_employment_type": self._clean_value(
                record.get("job_employment_type")
            ),

            "job_employment_types": self._clean_value(
                record.get("job_employment_types")
            ),

            "job_description": self._clean_value(
                record.get("job_description")
            ),

            "job_city": self._clean_value(
                record.get("job_city")
            ),

            "job_state": self._clean_value(
                record.get("job_state")
            ),

            "job_country": self._clean_value(
                record.get("job_country")
            ),

            "job_latitude": self._clean_value(
                record.get("job_latitude")
            ),

            "job_longitude": self._clean_value(
                record.get("job_longitude")
            ),

            "job_min_salary": self._clean_value(
                record.get("job_min_salary")
            ),

            "job_max_salary": self._clean_value(
                record.get("job_max_salary")
            ),

            "job_salary_period": self._clean_value(
                record.get("job_salary_period")
            ),

            "job_salary_currency": self._clean_value(
                record.get("job_salary_currency")
            ),

            "job_posted_at": self._clean_value(
                record.get("job_posted_at")
            ),

            "job_posted_at_datetime_utc":
                self._parse_datetime(
                    record.get(
                        "job_posted_at_datetime_utc"
                    )
                ),

            "job_is_remote": self._to_bool(
                record.get("job_is_remote")
            ),

            "job_apply_is_direct": self._to_bool(
                record.get("job_apply_is_direct")
            ),

            "job_highlights":
                self._serialize_value(
                    record.get("job_highlights")
                ),

            "apply_options_count":
                int(
                    self._clean_value(
                        record.get(
                            "apply_options_count"
                        )
                    )
                    or 0
                ),

            "job_apply_link": self._clean_value(
                record.get("job_apply_link")
            ),

            "job_google_link": self._clean_value(
                record.get("job_google_link")
            ),
        }

    # --------------------------------------------------------------
    # HELPERS
    # --------------------------------------------------------------

    @staticmethod
    def _clean_value(value):

        if value is None:
            return None

        try:
            if pd.isna(value):
                return None
        except (TypeError, ValueError):
            pass

        return value

    @staticmethod
    def _values_equal(old_value, new_value):

        # Both values are NULL
        if old_value is None and new_value is None:
            return True

        # One value is NULL and the other isn't
        if old_value is None or new_value is None:
            return False

        # Handle pandas / numpy NaN safely
        try:
            old_is_nan = pd.isna(old_value)
            new_is_nan = pd.isna(new_value)

            if old_is_nan and new_is_nan:
                return True

            if old_is_nan or new_is_nan:
                return False

        except (TypeError, ValueError):
            pass

        # Normalize pandas Timestamp
        if isinstance(old_value, pd.Timestamp):
            old_value = old_value.to_pydatetime()

        if isinstance(new_value, pd.Timestamp):
            new_value = new_value.to_pydatetime()

        # Normalize strings
        if isinstance(old_value, str):
            old_value = old_value.strip()

        if isinstance(new_value, str):
            new_value = new_value.strip()

        # Compare numbers safely
        if isinstance(old_value, (int, float)) and isinstance(
        new_value, (int, float)
        ):
            try:
                return float(old_value) == float(new_value)
            except (ValueError, TypeError):
                pass

        return old_value == new_value


    @staticmethod
    def _parse_datetime(value):

        value = JobWarehouseLoader._clean_value(value)

        if value is None:
            return None

        try:
            parsed = pd.to_datetime(
                value,
                utc=True,
            )

            if pd.isna(parsed):
                return None

            return parsed.to_pydatetime()

        except (ValueError, TypeError):
            return None

    
    @staticmethod
    def _to_bool(value):

        value = JobWarehouseLoader._clean_value(value)

        if value is None:
            return False

        if isinstance(value, bool):
            return value

        return str(value).strip().lower() in {
            "true",
            "1",
            "yes",
            "y",
        }

    @staticmethod
    def _serialize_value(value):

        value = JobWarehouseLoader._clean_value(value)

        if value is None:
            return None

        if isinstance(value, str):
            return value

        try:
            return json.dumps(value)

        except TypeError:
            return str(value)