import json

from src.monitoring.pipeline_monitor import PipelineMonitor


def test_successful_run_is_saved(tmp_path):
    monitor = PipelineMonitor(
        metrics_directory=str(tmp_path)
    )

    metrics = monitor.create_run("test_pipeline")
    metrics = monitor.complete_run(metrics)

    assert metrics["status"] == "SUCCESS"
    assert metrics["end_time"] is not None
    assert metrics["execution_time_seconds"] >= 0

    saved_file = (
        tmp_path / f"pipeline_run_{metrics['run_id']}.json"
    )

    assert saved_file.exists()

    saved_metrics = json.loads(
        saved_file.read_text(encoding="utf-8")
    )

    assert saved_metrics["status"] == "SUCCESS"


def test_failed_run_records_error(tmp_path):
    monitor = PipelineMonitor(
        metrics_directory=str(tmp_path)
    )

    metrics = monitor.create_run("test_pipeline")
    metrics = monitor.fail_run(
        metrics,
        RuntimeError("Simulated failure"),
    )

    assert metrics["status"] == "FAILED"
    assert metrics["error"] == "Simulated failure"

    saved_file = (
        tmp_path / f"pipeline_run_{metrics['run_id']}.json"
    )

    assert saved_file.exists()
