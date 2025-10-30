from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class JobListingSchema(BaseModel):
    """Schema for job listing data from job search platforms."""

    job_id: str
    title: str
    job_details_url: str
    job_summary: str
    company_name: str
    location: str
    country_code: str
    listing_date: datetime
    salary_label: Optional[str] = None
    work_type: Optional[str] = None
    job_classification: Optional[str] = None
    job_sub_classification: Optional[str] = None
    work_arrangements: Optional[str] = None


class JobDetailsSchema(BaseModel):
    """Schema for detailed job information and metadata."""

    job_id: str
    status: str
    is_expired: bool
    details: str
    is_verified: Optional[bool] = None
    expires_at: Optional[datetime] = None
