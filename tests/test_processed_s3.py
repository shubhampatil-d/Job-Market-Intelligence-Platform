import pandas as pd
import pytest

from src.config.settings import settings
from src.processing.job_processor import JobProcessor


def make_processor(tmp_path, monkeypatch, bucket=None):
    raw_path = tmp_path / "raw"
    processed_path = tmp_path / "processed"
    raw_path.mkdir()

    monkeypatch.setattr(settings, "RAW_DATA_PATH", raw_path)
    monkeypatch.setattr(settings, "PROCESSED_DATA_PATH", processed_path)
    monkeypatch.setattr(settings, "S3_RAW_BUCKET", bucket)
    monkeypatch.setattr(settings, "S3_PROCESSED_PREFIX", "processed/jobs")
    monkeypatch.setattr(settings, "AWS_REGION", "ap-south-1")

    return JobProcessor()


def test_processed_csv_uploads_to_s3(tmp_path, monkeypatch):
    processor = make_processor(
        tmp_path, monkeypatch, "job-market-intelligence-2026"
    )
    uploads = []

    class FakeS3Client:
        def upload_file(self, filename, bucket, key, ExtraArgs=None):
            uploads.append((filename, bucket, key, ExtraArgs))

    monkeypatch.setattr(
        "src.processing.job_processor.boto3.client",
        lambda service, region_name: FakeS3Client(),
    )

    dataframe = pd.DataFrame([
        {"job_id": "job-1", "job_title": "Data Engineer"}
    ])

    path = processor._save_processed_data(dataframe)

    assert path.exists()
    assert len(uploads) == 1

    filename, bucket, key, extra_args = uploads[0]
    assert filename == str(path)
    assert bucket == "job-market-intelligence-2026"
    assert key.startswith("processed/jobs/")
    assert key.endswith(path.name)
    assert extra_args == {"ContentType": "text/csv"}


def test_processed_csv_stays_local_when_s3_disabled(
    tmp_path, monkeypatch
):
    processor = make_processor(tmp_path, monkeypatch, bucket=None)

    dataframe = pd.DataFrame([
        {"job_id": "job-1", "job_title": "Data Engineer"}
    ])

    path = processor._save_processed_data(dataframe)

    assert path.exists()
    saved = pd.read_csv(path)
    assert saved.iloc[0]["job_id"] == "job-1"


def test_s3_upload_failure_preserves_processed_csv(
    tmp_path, monkeypatch
):
    processor = make_processor(
        tmp_path, monkeypatch, "job-market-intelligence-2026"
    )

    class FailingS3Client:
        def upload_file(self, *args, **kwargs):
            raise RuntimeError("Simulated S3 failure")

    monkeypatch.setattr(
        "src.processing.job_processor.boto3.client",
        lambda *args, **kwargs: FailingS3Client(),
    )

    dataframe = pd.DataFrame([
        {"job_id": "job-1", "job_title": "Data Engineer"}
    ])

    with pytest.raises(RuntimeError, match="Simulated S3 failure"):
        processor._save_processed_data(dataframe)

    files = list((tmp_path / "processed").rglob("*.csv"))
    assert len(files) == 1
    assert pd.read_csv(files[0]).iloc[0]["job_id"] == "job-1"