
import json

from src.state.processing_state_manager import ProcessingStateManager


def test_new_raw_file_is_eligible(tmp_path):
    manager = ProcessingStateManager(tmp_path / "processing_state.json")
    raw_file = tmp_path / "raw" / "jobs_001.json"
    raw_file.parent.mkdir()
    raw_file.write_text("[]", encoding="utf-8")

    assert manager.filter_unprocessed([raw_file]) == [raw_file]


def test_successfully_processed_file_is_skipped(tmp_path):
    manager = ProcessingStateManager(tmp_path / "processing_state.json")
    raw_file = tmp_path / "jobs_001.json"
    raw_file.write_text("[]", encoding="utf-8")

    manager.mark_processed([raw_file])

    assert manager.filter_unprocessed([raw_file]) == []


def test_uncheckpointed_file_remains_eligible_for_retry(tmp_path):
    manager = ProcessingStateManager(tmp_path / "processing_state.json")
    raw_file = tmp_path / "jobs_001.json"
    raw_file.write_text("[]", encoding="utf-8")

    # Simulate a processing/upload failure: do not mark it processed.
    assert manager.filter_unprocessed([raw_file]) == [raw_file]
    assert manager.filter_unprocessed([raw_file]) == [raw_file]


def test_processing_checkpoint_does_not_change_ingestion_state(tmp_path):
    ingestion_state_file = tmp_path / "pipeline_state.json"
    original_state = {
        "last_run": "2026-10-28T10:00:00",
        "last_cursor": None,
        "records_processed": 5,
        "pipeline_version": "1.0",
        "status": "SUCCESS",
    }
    ingestion_state_file.write_text(
        json.dumps(original_state),
        encoding="utf-8",
    )

    manager = ProcessingStateManager(tmp_path / "processing_state.json")
    raw_file = tmp_path / "jobs_001.json"
    raw_file.write_text("[]", encoding="utf-8")
    manager.mark_processed([raw_file])

    assert json.loads(ingestion_state_file.read_text(encoding="utf-8")) == original_state
    assert manager.state_file.exists()
