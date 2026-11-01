
import pandas as pd
import pytest
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker

from src.warehouse.loader import JobWarehouseLoader
from src.warehouse.models import Base, Job


@pytest.fixture
def warehouse(tmp_path):
    db_path = tmp_path / "test_warehouse.db"
    engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(engine)

    session_factory = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
    )
    loader = JobWarehouseLoader(
        engine=engine,
        session_factory=session_factory,
    )

    yield loader, session_factory
    engine.dispose()


def make_job(job_id="job-001", title="Data Engineer"):
    return {
        "job_id": job_id,
        "job_title": title,
        "employer_name": "Example Corp",
        "job_city": "Pune",
    }


def write_csv(tmp_path, records, name="jobs.csv"):
    path = tmp_path / name
    pd.DataFrame(records).to_csv(path, index=False)
    return path


def test_loader_inserts_new_job(warehouse, tmp_path):
    loader, session_factory = warehouse
    csv_path = write_csv(tmp_path, [make_job()])

    result = loader.load_csv(csv_path)

    assert result["records_inserted"] == 1
    assert result["records_updated"] == 0

    with session_factory() as session:
        assert session.query(Job).count() == 1
        assert session.query(Job).first().job_id == "job-001"


def test_loader_updates_existing_job(warehouse, tmp_path):
    loader, session_factory = warehouse

    first_csv = write_csv(tmp_path, [make_job()], "first.csv")
    loader.load_csv(first_csv)

    second_csv = write_csv(
        tmp_path,
        [make_job(title="Senior Data Engineer")],
        "second.csv",
    )
    result = loader.load_csv(second_csv)

    assert result["records_inserted"] == 0
    assert result["records_updated"] == 1

    with session_factory() as session:
        assert session.query(Job).count() == 1
        assert session.query(Job).first().job_title == "Senior Data Engineer"


def test_loader_skips_unchanged_job(warehouse, tmp_path):
    loader, session_factory = warehouse
    csv_path = write_csv(tmp_path, [make_job()])

    loader.load_csv(csv_path)
    result = loader.load_csv(csv_path)

    assert result["records_inserted"] == 0
    assert result["records_updated"] == 0
    assert result["records_skipped"] == 1

    with session_factory() as session:
        assert session.query(func.count(Job.id)).scalar() == 1



def test_loader_rolls_back_failed_batch(warehouse, tmp_path):
    loader, session_factory = warehouse

    csv_path = write_csv(
        tmp_path,
        [make_job("job-001"), make_job("job-002")],
    )

    def failing_session_factory():
        session = session_factory()

        def fail_commit():
            raise RuntimeError("Simulated commit failure")

        session.commit = fail_commit
        return session

    loader.session_factory = failing_session_factory

    with pytest.raises(RuntimeError, match="Simulated commit failure"):
        loader.load_csv(csv_path)

    # Both pending inserts must be rolled back.
    with session_factory() as session:
        assert session.query(Job).count() == 0
