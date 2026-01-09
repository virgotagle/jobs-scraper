# Jobs Scraper

A modern, async web scraper for job listings with built-in rate limiting, stealth browsing, and clean architecture. Currently supports Seek.co.nz with an extensible design for adding more job sites.

## ✨ Features

- **🚀 Async/Await Architecture**: High-performance asynchronous scraping
- **🕵️ Stealth Browsing**: Uses Playwright with stealth mode to avoid detection
- **⏱️ Built-in Rate Limiting**: Respectful scraping with configurable delays
- **🗄️ SQLite & PostgreSQL Support**: Flexible data storage with seamless switching
- **🔧 Clean Architecture**: Modular design following SOLID principles
- **📊 Data Validation**: Pydantic schemas ensure data integrity
- **🎯 Retry Logic**: Automatic retry with exponential backoff
- **🛠️ Extensible Design**: Easy to add new job sites via factory pattern
- **📝 Rich Logging**: Comprehensive logging with statistics
- **⚙️ Configuration-Driven**: Settings managed via `pyproject.toml`

## 🛠️ Tech Stack

- **Python 3.12+** with modern async/await patterns
- **Playwright** with stealth mode for browser automation
- **SQLAlchemy** for database ORM
- **PostgreSQL** & **SQLite** for data storage
- **Pydantic** for data validation and serialization
- **BeautifulSoup4** for HTML parsing
- **Tenacity** for retry logic
- **uv** for dependency management
- **Ruff** for linting and code quality

## 📦 Installation

### Prerequisites
- Python 3.12 or higher
- [uv](https://docs.astral.sh/uv/) package manager

### Setup
```bash
# Clone the repository
git clone <repository-url>
cd jobs-scraper

# Install dependencies using uv
uv sync

# Install Playwright browsers
uv run playwright install
```

## 🚀 Usage

### Basic Commands

```bash
# List available job sites
uv run python -m src.app --list-sites

# Scrape jobs by category (default mode)
uv run python -m src.app --site seek --by-category

# Scrape jobs by filter
uv run python -m src.app --site seek

# Custom rate limiting
uv run python -m src.app --site seek --by-category \
  --min-delay 1.0 --max-delay 3.0 --max-concurrent 1
```

### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--site` | Job site to scrape (`seek`) | Required |
| `--list-sites` | List all available job sites | - |
| `--by-category` | Scrape by category instead of filter | `false` |
| `--min-delay` | Minimum delay between requests (seconds) | From config |
| `--max-delay` | Maximum delay between requests (seconds) | From config |
| `--max-concurrent` | Maximum concurrent requests | From config |

## ⚙️ Configuration

Configuration is managed through `pyproject.toml`:

```toml
[tool.jobs-scrapers.sites.seek]
url = "https://www.seek.co.nz/"
location = "in-All-Auckland"
category = "jobs-in-information-communication-technology"
filter = "Python-Developer-jobs"

# Rate limiting settings
min_delay = 2.0        # Minimum seconds between requests
max_delay = 4.0        # Maximum seconds for random delays
max_concurrent = 2     # Maximum concurrent requests
```

### Customizing Search Parameters

- **Location**: Change `location` to target different areas (e.g., `"in-All-Wellington"`)
- **Category**: Modify `category` for different job categories
- **Filter**: Update `filter` for specific job types
- **Rate Limiting**: Adjust delays and concurrency for different scraping speeds

### 🗄️ Database Configuration

The application supports both **SQLite** (default) and **PostgreSQL**.

#### Using PostgreSQL
Create a `.env` file in the root directory:

```ini
POSTGRES_USERNAME=admin
POSTGRES_PASSWORD=admin
POSTGRES_DATABASE=jobs
POSTGRES_HOST=localhost
```

Or set the `DATABASE_URL` environment variable directly.

#### Using SQLite
Simply remove or comment out the `POSTGRES_*` variables in the `.env` file. The application will default to using `jobs.db` in the local directory.


## 🏗️ Architecture

### Project Structure
```
jobs-scraper/
├── src/
│   ├── core/                 # Core business logic
│   │   ├── config.py        # Configuration management
│   │   ├── enums.py         # Enumerations (JobSite)
│   │   ├── factory.py       # Scraper factory pattern
│   │   ├── models.py        # SQLAlchemy database models
│   │   ├── protocols.py     # Interface definitions
│   │   ├── rate_limiter.py  # Rate limiting implementation
│   │   ├── repositories.py  # Data access layer
│   │   ├── schemas.py       # Pydantic data schemas
│   │   └── utils/
│   │       └── browser.py   # Browser automation helper
│   ├── seek/                # Seek-specific implementation
│   │   ├── extractor.py     # Data extraction logic
│   │   └── scraper.py       # Seek scraper implementation
│   └── app.py               # CLI application entry point
├── test/                    # Test suite
├── database/               # SQLite database storage
├── pyproject.toml          # Project configuration
└── README.md
```

### Key Components

#### **Rate Limiter** (`src/core/rate_limiter.py`)
- Configurable delays between requests (2-4 seconds by default)
- Semaphore-based concurrency control
- Request statistics tracking
- Respects target website resources

#### **Browser Helper** (`src/core/utils/browser.py`)
- Playwright integration with stealth mode
- Session state management
- Robust resource cleanup
- Anti-detection features

#### **Repository Layer** (`src/core/repositories.py`)
- **Factory Pattern**: Automatically switches between SQLite and Postgres
- **BaseRepository**: Abstract interface for consistent data access
- **Self-Healing**: Auto-initializes database tables

#### **Data Models**
- **JobListingModel**: Job listing information
- **JobDetailsModel**: Detailed job descriptions
- **Pydantic Schemas**: Data validation and serialization

## 🗄️ Database Schema

The scraper stores data in SQLite with the following schema:

### job_listings
- `job_id` (Primary Key)
- `title`, `company_name`, `location`, `country_code`
- `job_details_url`, `job_summary`
- `listing_date`, `salary_label`, `work_type`
- `job_classification`, `job_sub_classification`, `work_arrangements`

### job_details
- `job_id` (Foreign Key → job_listings)
- `status`, `is_expired`, `is_verified`
- `details` (Markdown formatted), `expires_at`

## 🔍 Rate Limiting

The scraper implements respectful rate limiting to avoid overwhelming target websites:

- **Random Delays**: 2-4 seconds between requests (configurable)
- **Concurrency Control**: Maximum 2 simultaneous requests
- **Statistics Tracking**: Logs request counts and wait times
- **CLI Overrides**: Customize rate limiting via command line

### Rate Limiting Best Practices
- Use longer delays during peak hours
- Reduce concurrency for slower target sites
- Monitor logs for any rate limiting errors
- Respect robots.txt and website terms of service

## 🧪 Testing & Linting

```bash
# Run tests
uv run pytest

# Run linting
uv run ruff check .

# Run tests with coverage
uv run pytest --cov=src

# Run specific test
uv run pytest test/test_seek.py -v
```

### Continuous Integration
This project uses GitHub Actions for CI. The workflow (`.github/workflows/ci.yml`) automatically runs tests and linting on every push and pull request to `main`.

## 🚀 Adding New Job Sites

The scraper is designed for easy extension. To add a new job site:

1. **Add to JobSite enum** (`src/core/enums.py`):
```python
class JobSite(Enum):
    SEEK = "seek"
    NEW_SITE = "new_site"  # Add your site
```

2. **Create site-specific package** (`src/new_site/`):
```python
# src/new_site/extractor.py
class NewSiteExtractor:
    def extract_job_listings(self, html: str) -> list[JobListingSchema]: ...
    def extract_job_details(self, html: str) -> JobDetailsSchema: ...

# src/new_site/scraper.py  
class NewSiteScraper:
    def __init__(self, repository: RepositoryInterface): ...
    async def scrape(self, by_category: bool = False): ...
```

3. **Update factory** (`src/core/factory.py`):
```python
def get_scraper(job_site: JobSite, repository: RepositoryInterface):
    if job_site == JobSite.SEEK:
        return SeekScraper(repository)
    elif job_site == JobSite.NEW_SITE:
        return NewSiteScraper(repository)
```

4. **Add configuration** (`pyproject.toml`):
```toml
[tool.jobs-scrapers.sites.new_site]
url = "https://example.com/"
# ... site-specific settings
```

## 📊 Example Output

```bash
$ uv run python -m src.app --site seek --by-category

2025-10-31 11:41:42,402 - INFO - Starting job scraper for site: seek
2025-10-31 11:41:42,406 - INFO - Rate limiting: 2.0-4.0s delay, max 2 concurrent
2025-10-31 11:41:42,808 - INFO - Browser launched (headless=True, stealth=True)
2025-10-31 11:41:43,022 - INFO - Scraping page 1 for jobs-in-information-communication-technology in in-All-Auckland
2025-10-31 11:41:48,438 - INFO - Found 22 jobs on page 1
2025-10-31 11:41:50,123 - INFO - Page 1 complete. Moving to page 2
...
2025-10-31 11:45:30,555 - INFO - Scraping finished: 156 total jobs processed
2025-10-31 11:45:30,556 - INFO - Rate limiter stats: 78 requests, 145.2s total wait time, 1.9s avg wait time
```

## 🐛 Troubleshooting

### Common Issues

**Playwright browsers not installed:**
```bash
uv run playwright install
```

**Module not found errors:**
```bash
# Use the -m flag
uv run python -m src.app --list-sites
```

**Rate limiting too aggressive:**
```bash
# Reduce delays
uv run python -m src.app --site seek --min-delay 1.0 --max-delay 2.0
```

