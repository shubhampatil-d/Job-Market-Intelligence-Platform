import json

import pytest

from src.config.settings import settings
from src.ingestion.save_raw import RawDataSaver


def test_save_locally_when_s3_is_disabled(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "RAW_DATA_PATH", tmp_path)
    monkeypatch.setattr(settings, "S3_RAW_BUCKET", None)

    saver = RawDataSaver()
    jobs = [{"title": "Data Engineer", "company": "Example"}]

    path = saver.save(jobs)

    assert path.exists()
    assert json.loads(path.read_text(encoding="utf-8")) == jobs


def test_save_uploads_json_to_s3(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "RAW_DATA_PATH", tmp_path)
    monkeypatch.setattr(
        settings, "S3_RAW_BUCKET", "job-market-intelligence-2026"
    )
    monkeypatch.setattr(settings, "S3_RAW_PREFIX", "raw/jobs")
    monkeypatch.setattr(settings, "AWS_REGION", "ap-south-1")

    uploads = []

    class FakeS3Client:
        def upload_file(self, filename, bucket, key, ExtraArgs=None):
            uploads.append((filename, bucket, key, ExtraArgs))

    monkeypatch.setattr(
        "src.ingestion.save_raw.boto3.client",
        lambda service, region_name: FakeS3Client(),
    )

    saver = RawDataSaver()
    path = saver.save([{"title": "Data Engineer"}])

    assert path.exists()
    assert len(uploads) == 1

    filename, bucket, key, extra_args = uploads[0]

    assert filename == str(path)
    assert bucket == "job-market-intelligence-2026"
    assert key.startswith("raw/jobs/")
    assert key.endswith(path.name)
    assert extra_args == {"ContentType": "application/json"}


def test_s3_failure_raises_and_keeps_local_file(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "RAW_DATA_PATH", tmp_path)
    monkeypatch.setattr(
        settings, "S3_RAW_BUCKET", "job-market-intelligence-2026"
    )

    class FailingS3Client:
        def upload_file(self, *args, **kwargs):
            raise RuntimeError("Simulated S3 failure")

    monkeypatch.setattr(
        "src.ingestion.save_raw.boto3.client",
        lambda *args, **kwargs: FailingS3Client(),
    )

    saver = RawDataSaver()

    with pytest.raises(RuntimeError, match="Simulated S3 failure"):
        saver.save([{"title": "Data Engineer"}])

    # Local copy remains available for recovery.
    files = list(tmp_path.rglob("*.json"))
    assert len(files) == 1
    assert json.loads(files[0].read_text(encoding="utf-8")) == [
        {"title": "Data Engineer"}
    ]