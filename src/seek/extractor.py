import datetime
import html
import json
import logging
import re

from bs4 import BeautifulSoup
from markdownify import markdownify as md  # type: ignore

from src.core.schemas import JobDetailsSchema, JobListingSchema


class SeekExtractor:
    """Extract job data from Seek.co.nz HTML pages."""

    def _extract_seek_redux_data(self, html: str) -> dict:
        """Extract Redux state data from Seek's window.SEEK_REDUX_DATA JavaScript variable."""
        soup = BeautifulSoup(html, "html.parser")
        script_tags = soup.find_all("script")
        for script in script_tags:
            script_text = script.get_text()
            # Search for the Redux data pattern in script tags
            match = re.search(
                r"window\.SEEK_REDUX_DATA\s*=\s*(\{.*?\});", script_text, re.DOTALL
            )
            if match:
                json_str = match.group(1)
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    logging.warning(
                        "Failed to decode SEEK_REDUX_DATA JSON, returning empty dict"
                    )
                    return {}
        return {}

    def _format_datetime(self, date_str: str) -> datetime.datetime:
        """Convert ISO date string to datetime, handling timezone suffixes."""
        try:
            # Replace 'Z' with UTC offset for proper parsing
            return datetime.datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except ValueError:
            logging.warning(f"Invalid date format '{date_str}', using current time")
            return datetime.datetime.now()

    def _format_job_listings(self, data: dict) -> list[JobListingSchema]:
        """Transform raw job listing data into structured JobListingSchema objects."""
        if job_list := data.get("results", {}).get("results", {}).get("jobs", []):
            return [
                JobListingSchema(
                    job_id=job.get("id", ""),
                    title=job.get("title", ""),
                    job_details_url=f"https://www.seek.co.nz/job/{job.get('id', '')}",
                    job_summary=job.get("teaser", ""),
                    company_name=job.get("companyName", ""),
                    location=",".join(
                        [x.get("label", "") for x in job.get("locations", [])]
                    ),
                    country_code=job.get("locations", [])[0]["countryCode"],
                    listing_date=self._format_datetime(job.get("listingDate", None)),
                    salary_label=job.get("salaryLabel", None),
                    work_type=",".join(job.get("workTypes", None)),
                    job_classification=",".join(
                        [
                            x.get("classification", {}).get("description", "")
                            for x in job.get("classifications", [])
                        ]
                    ),
                    job_sub_classification=",".join(
                        [
                            x.get("subclassification", {}).get("description", "")
                            for x in job.get("classifications", [])
                        ]
                    ),
                    work_arrangements=job.get("workArrangements", {}).get(
                        "displayText", ""
                    ),
                )
                for job in job_list
            ]
        return []

    def _format_job_details(self, data: dict) -> JobDetailsSchema:
        """Transform raw job detail data into structured JobDetailsSchema object."""
        job_details = data.get("jobdetails", {}).get("result", {}).get("job", None)
        return JobDetailsSchema(
            job_id=job_details.get("id", ""),
            status=job_details.get("status", ""),
            is_expired=job_details.get("isExpired", True),
            details=self._html_to_clean_markdown(job_details.get("content", "")),
            is_verified=job_details.get("isVerified", None),
            expires_at=self._format_datetime(
                job_details.get("expiresAt", {}).get("dateTimeUtc", None)
            ),
        )

    def extract_job_listings(self, html: str) -> list[JobListingSchema]:
        """Extract job listings from Seek search results HTML."""
        return self._format_job_listings(self._extract_seek_redux_data(html))

    def extract_job_details(self, html: str) -> JobDetailsSchema:
        """Extract job details from Seek job detail page HTML."""
        return self._format_job_details(self._extract_seek_redux_data(html))

    def _html_to_clean_markdown(self, html_text):
        """Convert HTML to markdown with proper UTF-8 handling."""
        # Decode HTML entities (&#55357;&#56524; -> \ud83d\udccc)
        decoded = html.unescape(html_text)

        # Fix UTF-16 surrogates to proper Unicode characters (-> 📌)
        try:
            fixed = decoded.encode("utf-16", "surrogatepass").decode("utf-16")
        except (UnicodeDecodeError, UnicodeEncodeError):
            # Fallback: ignore problematic characters
            fixed = decoded.encode("utf-8", "ignore").decode("utf-8")

        # Convert to markdown
        markdown = md(fixed)

        return markdown
