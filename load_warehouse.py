from pathlib import Path
from pprint import pprint

from src.warehouse.loader import JobWarehouseLoader


BASE_DIR = Path(__file__).resolve().parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"


def find_latest_processed_csv():
    csv_files = list(PROCESSED_DIR.rglob("processed_jobs_*.csv"))

    if not csv_files:
        raise FileNotFoundError(
            f"No processed CSV files found in: {PROCESSED_DIR}"
        )

    return max(csv_files, key=lambda file: file.stat().st_mtime)


def main():

    csv_path = find_latest_processed_csv()

    print("Initializing warehouse...")
    loader = JobWarehouseLoader()
    loader.initialize_database()

    print("\nLoading processed jobs...")
    print(f"CSV file: {csv_path}")

    result = loader.load_csv(csv_path)

    print("\nWarehouse load result:")
    pprint(result)


if __name__ == "__main__":
    main()