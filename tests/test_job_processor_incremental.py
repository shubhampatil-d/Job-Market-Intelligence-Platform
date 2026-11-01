import pandas as pd
import pytest
from src.config.settings import settings
from src.processing.job_processor import JobProcessor



def test_clean_dataframe_handles_missing_required_column(tmp_path, monkeypatch):
    processor = make_processor(tmp_path, monkeypatch)

    dataframe = pd.DataFrame([
        {"job_id": "job-1", "employer_name": "Example Ltd"},
        {"job_id": "job-2", "employer_name": "Another Ltd"},
    ])

    with pytest.raises(ValueError, match="Missing required columns"):
        processor._clean_dataframe(dataframe)




def make_processor(tmp_path, monkeypatch):
    raw_path = tmp_path / "raw"
    processed_path = tmp_path / "processed"

    raw_path.mkdir()

    monkeypatch.setattr(
        settings, "RAW_DATA_PATH", raw_path
    )
    monkeypatch.setattr(
        settings, "PROCESSED_DATA_PATH", processed_path
    )

    return JobProcessor()


def test_deduplicate_keeps_last_record(tmp_path, monkeypatch):
    processor = make_processor(tmp_path, monkeypatch)

    dataframe = pd.DataFrame([
        {"job_id": "job-1", "job_title": "Junior Engineer"},
        {"job_id": "job-1", "job_title": "Data Engineer"},
        {"job_id": "job-2", "job_title": "Analyst"},
    ])

    result = processor._deduplicate(dataframe)

    assert len(result) == 2

    job = result.loc[result["job_id"] == "job-1"].iloc[0]
    assert job["job_title"] == "Data Engineer"


def test_clean_dataframe_removes_missing_required_values(
    tmp_path, monkeypatch
):
    processor = make_processor(tmp_path, monkeypatch)

    dataframe = pd.DataFrame([
        {
            "job_id": "job-1",
            "job_title": "Data Engineer",
            "employer_name": "Example Ltd",
        },
        {
            "job_id": "job-2",
            "job_title": None,
            "employer_name": "Example Ltd",
        },
    ])

    result = processor._clean_dataframe(dataframe)

    assert len(result) == 1
    assert result.iloc[0]["job_id"] == "job-1"



def test_deduplicate_does_not_remove_distinct_jobs(tmp_path, monkeypatch):
    processor = make_processor(tmp_path, monkeypatch)

    dataframe = pd.DataFrame([
        {"job_id": "job-1", "job_title": "Data Engineer"},
        {"job_id": "job-2", "job_title": "Python Developer"},
        {"job_id": "job-3", "job_title": "Data Analyst"},
    ])

    result = processor._deduplicate(dataframe)

    assert len(result) == 3
    assert result["job_id"].nunique() == 3

import json

import pytest

from src.processing.job_processor import JobProcessor
from src.state.processing_state_manager import ProcessingStateManager


class FakeS3Client:
    def __init__(self, should_fail=False):
        self.should_fail = should_fail
        self.uploads = []

    def upload_file(self, filename, bucket, key, ExtraArgs=None):
        if self.should_fail:
            raise RuntimeError("Simulated S3 upload failure")

        self.uploads.append((filename, bucket, key, ExtraArgs))


def create_processor(tmp_path, should_fail=False):
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()

    raw_file = raw_dir / "jobs_test.json"
    raw_file.write_text(
        json.dumps([
            {
                "job_id": "job-001",
                "job_title": "Data Engineer",
                "employer_name": "Example Corp",
                "job_city": "Pune",
            }
        ]),
        encoding="utf-8",
    )

    processor = JobProcessor()
    processor.raw_path = raw_dir
    processor.processed_path = tmp_path / "processed"
    processor.processed_path.mkdir()

    processor.state_manager = ProcessingStateManager(
        tmp_path / "state" / "processing_state.json"
    )

    processor.s3_bucket = "test-bucket"
    processor.s3_prefix = "processed/jobs"
    processor._s3_client = FakeS3Client(should_fail=should_fail)

    return processor, raw_file


def test_new_file_is_processed_and_not_processed_twice(tmp_path):
    processor, raw_file = create_processor(tmp_path)

    output_path, metrics = processor.run()

    assert output_path is not None
    assert output_path.exists()
    assert metrics["records_fetched"] == 1
    assert metrics["records_processed"] == 1
    assert len(processor._s3_client.uploads) == 1

    # The input file should now be checkpointed.
    assert processor.state_manager.filter_unprocessed([raw_file]) == []

    # A second run should skip the file and not upload another CSV.
    second_output, second_metrics = processor.run()

    assert second_output is None
    assert second_metrics["records_processed"] == 0
    assert len(processor._s3_client.uploads) == 1


def test_s3_failure_leaves_new_file_eligible_for_retry(tmp_path):
    processor, raw_file = create_processor(
        tmp_path,
        should_fail=True,
    )

    with pytest.raises(RuntimeError, match="Simulated S3 upload failure"):
        processor.run()

    # The local CSV should be preserved, but the input must not
    # be checkpointed because the S3 upload failed.
    assert list(processor.processed_path.rglob("*.csv"))
    assert processor.state_manager.filter_unprocessed([raw_file]) == [
        raw_file
    ]
