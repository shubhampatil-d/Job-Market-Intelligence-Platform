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
