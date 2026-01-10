# Jobs Scraper

[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![Code Style: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> A CLI tool that aggregates job data from sites like Seek by implementing a two-stage asynchronous scraping pipeline with configurable rate limiting, designed for robust data collection and analysis.

**Built with**: 🐍 Python 3.12+ • 🎭 Playwright • 🗄️ SQLAlchemy • ⚡ uv

## Overview

**Jobs Scraper** solves the challenge of manually aggregating job list data for [Recruiters/Data Analysts]. Traditional scraping approaches are often detected or brittle; this tool implements a robust, stealthy pipeline that respects site limits while ensuring data integrity.

The system implements a **Two-Stage Pipeline** architecture. First, it discovers and stores job listings. Second, it asynchronously fetches detailed descriptions for each listing. This separation ensures that network interruptions don't cause data loss—the process can be resumed at any time.

Key design decisions include:

- **Stealth Automation**: Uses `playwright-stealth` to mimic real user behavior and avoid bot detection mechanisms.
- **Repository Pattern**: Abstracts data storage, allowing seamless switching between SQLite (local development) and PostgreSQL (production).
- **Factory Pattern**: Enables easy extension to support new job sites (e.g., LinkedIn, Indeed) without modifying core logic.

## Features

### Core

- ✅ **Two-Stage Scraping**: Decoupled listing discovery and detail extraction.
- ✅ **Resumable Operations**: Tracks progress in DB; crashes don't mean restarting from zero.
- ✅ **Multi-Database Support**: First-class support for both SQLite and PostgreSQL.

### Integrations

- ✅ **Seek.co.nz**: Full support for job search filtration and detail extraction.
- 🚧 **LinkedIn**: Planned support.

### Operations

- ✅ **Rate Limiting**: Configurable random delays and concurrency limits (Semaphore-based).
- ✅ **Stealth Mode**: Automated browser fingerprint masking.
- ✅ **Structured Logging**: Detailed execution logs for debugging.

## Architecture

### Project Structure

```
jobs-scraper/
├── src/
│   ├── app.py               # CLI entry point
│   ├── core/                # Domain logic & Interfaces
│   │   ├── entities.py      # (Implied by protocols/models)
│   │   ├── factory.py       # Scraper instantiation logic
│   │   ├── models.py        # SQLAlchemy ORM definitions
│   │   ├── protocols.py     # Scraper/Repo interfaces
│   │   ├── rate_limiter.py  # Concurrency control
│   │   ├── repositories.py  # Data access implementations
│   │   └── utils/           # Shared utilities (Browser, etc)
│   └── seek/                # Seek.co.nz implementation
│       ├── extractor.py     # HTML parsing logic
│       └── scraper.py       # Site-specific orchestration
├── test/                    # Pytest suite
├── pyproject.toml           # Config & Dependencies
└── jobs.db                  # Default local database
```

### Core Components

| Component              | Location                    | Responsibility                                         |
| :--------------------- | :-------------------------- | :----------------------------------------------------- |
| **JobScraperFactory**  | `src/core/factory.py`       | Instantiates site-specific scrapers based on CLI args. |
| **SeekScraper**        | `src/seek/scraper.py`       | Implements the scrape workflow for Seek.co.nz.         |
| **PostgresRepository** | `src/core/repositories.py`  | Handles data persistence for PostgreSQL.               |
| **BrowserHelper**      | `src/core/utils/browser.py` | Manages Playwright lifecycle and stealth contexts.     |

## Tech Stack & Patterns

### Tech Stack

| Category       | Technology     | Version  | Purpose                                 |
| :------------- | :------------- | :------- | :-------------------------------------- |
| **Language**   | Python         | 3.12+    | Core runtime.                           |
| **Automation** | Playwright     | ^1.55    | Headless browser automation.            |
| **ORM**        | SQLAlchemy     | ^2.0     | Database abstraction.                   |
| **Parsing**    | BeautifulSoup4 | ^4.14    | HTML content extraction.                |
| **Resilience** | Tenacity       | ^9.1     | Retry logic with backoff.               |
| **Management** | uv             | _latest_ | Fast Python package installer/resolver. |

### Design Patterns

| Pattern               | Location                   | Rationale                                                                                  |
| :-------------------- | :------------------------- | :----------------------------------------------------------------------------------------- |
| **Repository**        | `src/core/repositories.py` | Decouples business logic from database implementation (SQLite vs Postgres).                |
| **Factory**           | `src/core/factory.py`      | Centralizes creation of scraper instances, simplifying the addition of new sites.          |
| **Strategy/Protocol** | `src/core/protocols.py`    | Defines a strict interface (`ScraperInterface`) that all site implementations must follow. |

## Getting Started

### Prerequisites

| Requirement | Version | Check Command                 |
| :---------- | :------ | :---------------------------- |
| Python      | 3.12+   | `python --version`            |
| uv          | 0.4+    | `uv --version`                |
| Playwright  | \*      | `uv run playwright --version` |

### Installation

1.  **Clone the repository**:

    ```bash
    git clone https://github.com/your-org/jobs-scraper.git
    cd jobs-scraper
    ```

2.  **Install dependencies**:

    ```bash
    uv sync
    ```

3.  **Install browser binaries**:
    ```bash
    uv run playwright install
    ```

### Configuration

Configuration is managed via `pyproject.toml` (for defaults) and Environment Variables (for secrets/DB).

**1. Database Setup (Optional)**
By default, the app uses `jobs.db` (SQLite). To use PostgreSQL, create a `.env` file:

```ini
# .env
DATABASE_URL=postgresql://user:pass@localhost:5432/jobs_db
# OR
POSTGRES_USERNAME=admin
POSTGRES_PASSWORD=secret
POSTGRES_HOST=localhost
POSTGRES_DATABASE=jobs
```

**2. Scraper Defaults**
Edit `[tool.jobs-scrapers.sites.seek]` in `pyproject.toml` to change default search parameters (URL, category, filters).

### Verify Installation

Run a quick status check by listing available sites:

```bash
uv run python -m src.app --list-sites
# Expected output:
# Available job sites:
#   - seek
```

## Usage

### CLI Commands

**Scrape Jobs (Default Mode)**
Scrapes using the `filter` defined in configuration.

```bash
uv run python -m src.app --site seek
```

**Scrape by Category**
Uses the broad category search instead of a specific keyword filter.

```bash
uv run python -m src.app --site seek --by-category
```

**Custom Rate Limiting**
Override config defaults for aggressive or polite scraping.

```bash
uv run python -m src.app --site seek \
  --min-delay 5.0 \
  --max-delay 10.0 \
  --max-concurrent 1
```

### Data Access

The data is stored in the `job_listings` and `job_details` tables.

**Python Access:**

```python
from src.core.repositories import SQLiteRepository

repo = SQLiteRepository("sqlite:///jobs.db")
# Get listings that still need details
pending = repo.get_listings_missing_details()
print(f"Pending scrape: {len(pending)}")
```

## Development

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage report
uv run pytest --cov=src --cov-report=html
```

### Code Quality

We strictly enforce type hints and linting rules.

```bash
# Format code
uv run ruff format .

# Check for linting errors
uv run ruff check .

# Fix auto-fixable errors
uv run ruff check --fix .
```

### Adding a New Site

1.  **Define Enum**: Add new site to `JobSite` in `src/core/enums.py`.
2.  **Implement Extractor**: Create `src/newsite/extractor.py` implementing `ExtractorInterface`.
3.  **Implement Scraper**: Create `src/newsite/scraper.py` implementing `ScraperInterface`.
4.  **Register Factory**: Update `JobScraperFactory` in `src/core/factory.py` to return your new scraper.
5.  **Add Config**: Add `[tool.jobs-scrapers.sites.newsite]` to `pyproject.toml`.

## Deployment

### Production Considerations

- **Schedule**: Run via `cron` or a task scheduler (e.g., Airflow).
- **Database**: robust PostgreSQL instance recommended for >10k listings.
- **Concurrency**: Set `--max-concurrent` based on your machine's CPU/RAM (Browser instances are heavy).
- **Headless**: The app runs headless by default. Ensure your environment has necessary system dependencies for Playwright (or use the official Playwright Docker image).

## Troubleshooting

### Common Issues

<details>
<summary><strong>Playwright Error: "Executable doesn't exist"</strong></summary>

**Cause**: Browser binaries were not installed after `uv sync`.

**Solution**:

```bash
uv run playwright install
```

</details>

<details>
<summary><strong>Database Error: "no such table: job_listings"</strong></summary>

**Cause**: Repository failed to initialize or DB file path is invalid. The app auto-creates tables on init.

**Solution**:
Check permissions on the directory. Delete `jobs.db` to force recreation if using SQLite.

</details>

<details>
<summary><strong>Scraper Hangs/Timeout</strong></summary>

**Cause**: Target site may be blocking requests or loading is slow.

**Solution**:
Increase delays with `--min-delay 5` or reduce concurrency with `--max-concurrent 1`.

</details>

## License

This project is licensed under the MIT License.
