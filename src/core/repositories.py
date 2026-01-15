"""SQLite and Postgres repositories for job data storage."""

import logging
import os
from abc import ABC, abstractmethod
from typing import Optional

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from .models import Base, JobDetailsModel, JobListingModel
from .schemas import JobDetailsSchema, JobListingSchema

load_dotenv()


class BaseRepository(ABC):
    """Abstract base class for job repositories."""

    @abstractmethod
    def insert_listing_with_details(
        self, listing_schema: JobListingSchema, details_schema: JobDetailsSchema
    ):
        """Insert or update job listing and details in database."""
        pass

    @abstractmethod
    def insert_job_listing(self, listing_schema: JobListingSchema):
        """Insert job listing only."""
        pass

    @abstractmethod
    def get_listings_missing_details(self) -> list[JobListingSchema]:
        """Get job listings that don't have details yet."""
        pass

    @abstractmethod
    def close(self):
        """Close database connection."""
        pass


class SQLiteRepository(BaseRepository):
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

    def insert_job_listing(self, listing_schema: JobListingSchema):
        """Insert job listing only."""
        with Session(self.engine) as session:
            try:
                existing_listing = session.get(JobListingModel, listing_schema.job_id)
                if existing_listing:
                    for key, value in listing_schema.model_dump().items():
                        setattr(existing_listing, key, value)
                else:
                    listing = JobListingModel(**listing_schema.model_dump())
                    session.add(listing)
                session.commit()
            except Exception as e:
                session.rollback()
                logging.error(
                    f"Failed to insert job listing {listing_schema.job_id}: {e}"
                )
                raise RuntimeError(f"Failed to insert job listing: {e}") from e

    def get_listings_missing_details(self) -> list[JobListingSchema]:
        """Get job listings that don't have details yet."""
        with Session(self.engine) as session:
            # Query listings that don't have a corresponding details entry
            listings = (
                session.query(JobListingModel)
                .outerjoin(JobDetailsModel)
                .filter(JobDetailsModel.job_id.is_(None))
                .all()
            )
            return [
                JobListingSchema.model_validate(listing, from_attributes=True)
                for listing in listings
            ]

    def close(self):
        """Close database connection and clean up resources."""
        self.engine.dispose()


class PostgresRepository(BaseRepository):
    """PostgreSQL database repository for job listings and details."""

    def __init__(self, db_url: Optional[str] = None) -> None:
        """Initialize repository with database connection.

        Args:
            db_url: Database URL. If not provided, reads from DATABASE_URL
                   or constructs from POSTGRES_* env vars.
        """
        self.db_url = db_url or os.getenv("DATABASE_URL")

        if not self.db_url:
            user = os.getenv("POSTGRES_USERNAME")
            password = os.getenv("POSTGRES_PASSWORD")
            host = os.getenv("POSTGRES_HOST")
            db = os.getenv("POSTGRES_DATABASE")
            if user and password and host and db:
                self.db_url = f"postgresql://{user}:{password}@{host}/{db}"

        if not self.db_url:
            raise ValueError(
                "Database URL must be provided or set in DATABASE_URL environment variable, "
                "or configured via POSTGRES_USERNAME, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_DATABASE."
            )

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

    def insert_job_listing(self, listing_schema: JobListingSchema):
        """Insert job listing only."""
        with Session(self.engine) as session:
            try:
                existing_listing = session.get(JobListingModel, listing_schema.job_id)
                if existing_listing:
                    for key, value in listing_schema.model_dump().items():
                        setattr(existing_listing, key, value)
                else:
                    listing = JobListingModel(**listing_schema.model_dump())
                    session.add(listing)
                session.commit()
            except Exception as e:
                session.rollback()
                logging.error(
                    f"Failed to insert job listing {listing_schema.job_id}: {e}"
                )
                raise RuntimeError(f"Failed to insert job listing: {e}") from e

    def get_listings_missing_details(self) -> list[JobListingSchema]:
        """Get job listings that don't have details yet."""
        with Session(self.engine) as session:
            # Query listings that don't have a corresponding details entry
            listings = (
                session.query(JobListingModel)
                .outerjoin(JobDetailsModel)
                .filter(JobDetailsModel.job_id.is_(None))
                .all()
            )
            return [
                JobListingSchema.model_validate(listing, from_attributes=True)
                for listing in listings
            ]

    def close(self):
        """Close database connection and clean up resources."""
        self.engine.dispose()


def get_repository() -> BaseRepository:
    """Get the appropriate repository based on environment configuration.

    Returns:
        BaseRepository: Either PostgresRepository or SQLiteRepository.
    """
    # Check for Postgres configuration
    if os.getenv("DATABASE_URL") or (
        os.getenv("POSTGRES_USERNAME")
        and os.getenv("POSTGRES_PASSWORD")
        and os.getenv("POSTGRES_DATABASE")
    ):
        return PostgresRepository()

    # Default to SQLite
    return SQLiteRepository()
