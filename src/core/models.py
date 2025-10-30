"""SQLAlchemy models for job scraper database."""

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class JobListingModel(Base):
    """Job listing information from job sites."""

    __tablename__ = "job_listings"

    job_id = Column(String, primary_key=True)
    title = Column(String)
    job_details_url = Column(String)
    job_summary = Column(Text)
    company_name = Column(String)
    location = Column(String)
    country_code = Column(String)
    listing_date = Column(DateTime)
    salary_label = Column(String, nullable=True)
    work_type = Column(String, nullable=True)
    job_classification = Column(String, nullable=True)
    job_sub_classification = Column(String, nullable=True)
    work_arrangements = Column(String, nullable=True)

    # Relationship to JobDetailsModel
    details = relationship("JobDetailsModel", back_populates="listing")


class JobDetailsModel(Base):
    """Detailed job information and metadata."""

    __tablename__ = "job_details"

    job_id = Column(String, ForeignKey("job_listings.job_id"), primary_key=True)
    status = Column(String)
    is_expired = Column(Boolean)
    details = Column(Text)
    is_verified = Column(Boolean, nullable=True)
    expires_at = Column(DateTime, nullable=True)

    # Relationship back to JobListingModel
    listing = relationship("JobListingModel", back_populates="details")
