
"""
Run the Job Market Intelligence processing pipeline.
"""

from pprint import pprint

from src.monitoring.pipeline_monitor import PipelineMonitor
from src.processing.job_processor import JobProcessor


def main():
    monitor = PipelineMonitor()
    metrics = monitor.create_run(
        pipeline_name="job_processing"
    )

    try:
        processor = JobProcessor()
        output_path, processing_metrics = processor.run()

        monitor.update_metrics(
            metrics,
            records_fetched=processing_metrics["records_fetched"],
            records_valid=processing_metrics["records_valid"],
            records_rejected=processing_metrics["records_rejected"],
            records_processed=processing_metrics["records_processed"],
            records_failed=processing_metrics["records_failed"],
            duplicates_removed=processing_metrics["duplicates_removed"],
            output_path=str(output_path) if output_path else None,
        )

        metrics = monitor.complete_run(metrics)

        if output_path:
            print("\nPipeline completed successfully.")
            print(f"Output: {output_path}")
        else:
            print(
                "\nPipeline completed successfully. "
                "No new raw files to process."
            )

        print("\nRun metrics:")
        pprint(metrics)

    except Exception as exc:
        monitor.fail_run(metrics, exc)
        print("\nPipeline failed.")
        raise


if __name__ == "__main__":
    main()
