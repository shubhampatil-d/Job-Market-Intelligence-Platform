from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Job(Base):
    __tablename__ = "fact_jobs"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    job_id = Column(
        String(500),
        nullable=False,
        index=True,
    )

    job_title = Column(
        String(500),
        nullable=False,
    )

    employer_name = Column(
        String(300),
        nullable=False,
        index=True,
    )

    employer_logo = Column(
        Text,
        nullable=True,
    )

    job_publisher = Column(
        String(300),
        nullable=True,
    )

    job_employment_type = Column(
        String(100),
        nullable=True,
    )

    job_employment_types = Column(
        Text,
        nullable=True,
    )

    job_description = Column(
        Text,
        nullable=True,
    )

    job_city = Column(
        String(200),
        nullable=True,
        index=True,
    )

    job_state = Column(
        String(200),
        nullable=True,
    )

    job_country = Column(
        String(100),
        nullable=True,
        index=True,
    )

    job_latitude = Column(
        Float,
        nullable=True,
    )

    job_longitude = Column(
        Float,
        nullable=True,
    )

    job_min_salary = Column(
        Float,
        nullable=True,
    )

    job_max_salary = Column(
        Float,
        nullable=True,
    )

    job_salary_period = Column(
        String(50),
        nullable=True,
    )

    job_salary_currency = Column(
        String(20),
        nullable=True,
    )

    job_posted_at = Column(
        String(100),
        nullable=True,
    )

    job_posted_at_datetime_utc = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    job_is_remote = Column(
        Boolean,
        nullable=False,
        default=False,
    )

    job_apply_is_direct = Column(
        Boolean,
        nullable=False,
        default=False,
    )

    job_highlights = Column(
        Text,
        nullable=True,
    )

    apply_options_count = Column(
        Integer,
        nullable=False,
        default=0,
    )

    job_apply_link = Column(
        Text,
        nullable=True,
    )

    job_google_link = Column(
        Text,
        nullable=True,
    )

    __table_args__ = (
        UniqueConstraint(
            "job_id",
            name="uq_fact_jobs_job_id",
        ),
    )