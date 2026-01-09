import logging
import os
import sys

from sqlalchemy import text

# Add src to path
sys.path.append("src")

from dotenv import load_dotenv

from core.repositories import get_repository
from core.schemas import JobDetailsSchema, JobListingSchema

load_dotenv()


# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def verify_connection():
    logger.info("Getting repository from factory...")

    try:
        repo = get_repository()
        logger.info(f"Initialized repository type: {type(repo).__name__}")

        # Test connection
        if hasattr(repo, "engine"):
            with repo.engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                logger.info(f"Connection test result: {result.scalar()}")

        repo.close()
        logger.info("Successfully closed repository")

    except Exception as e:
        logger.error(f"Verification failed: {e}")


if __name__ == "__main__":
    verify_connection()
