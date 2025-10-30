"""SQLite repository for job data storage."""

import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from .models import Base, JobDetailsModel, JobListingModel
from .schemas import JobDetailsSchema, JobListingSchema


class SQLiteRepository:
    """SQLite database repository for job listings and details."""

    def __init__(self, db_url: str = "sqlite:///jobs.db") -> None:
        """Initialize repository with database connection."""
        self.db_url = db_url

        try:
            self.engine = create_engine(self.db_url)
            Base.metadata.create_all(self.engine)
        except Exception as e:
            logging.error(f"Failed to initialize database at {self.db_url}: {e}")
            raise RuntimeError(f"Failed to initialize database: {e}") from e

    def insert_listing_with_details(
        self, listing_schema: JobListingSchema, details_schema: JobDetailsSchema
    ):
        """Insert or update job listing and details in database."""
        with Session(self.engine) as session:
            try:
                # Update existing listing or create new one
                existing_listing = session.get(JobListingModel, listing_schema.job_id)
                if existing_listing:
                    for key, value in listing_schema.model_dump().items():
                        setattr(existing_listing, key, value)
                else:
                    listing = JobListingModel(**listing_schema.model_dump())
                    session.add(listing)

                # Update existing details or create new one
                existing_details = session.get(JobDetailsModel, details_schema.job_id)
                if existing_details:
                    for key, value in details_schema.model_dump().items():
                        setattr(existing_details, key, value)
                else:
                    details = JobDetailsModel(**details_schema.model_dump())
                    session.add(details)

                session.commit()
            except Exception as e:
                session.rollback()
                logging.error(f"Failed to insert job {listing_schema.job_id}: {e}")
                raise RuntimeError(f"Failed to insert job data: {e}") from e

    def close(self):
        """Close database connection and clean up resources."""
        self.engine.dispose()
