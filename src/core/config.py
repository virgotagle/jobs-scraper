"""Configuration loader for the jobs scraper application."""

import tomllib

# Load configuration from pyproject.toml
with open("pyproject.toml", "rb") as f:
    pyproject_data = tomllib.load(f)

config = pyproject_data["tool"]["jobs-scrapers"]
