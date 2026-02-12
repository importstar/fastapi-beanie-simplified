# Testing Guide

This project uses `pytest` for unit and integration testing.

## Prerequisites

- Python 3.12+
- MongoDB running locally on `localhost:27017` (or configured via `DATABASE_URI`)

## Running Tests

1. Ensure your virtual environment is activated:
   ```bash
   source venv/bin/activate
   ```

2. Run tests using `pytest`:
   ```bash
   pytest
   ```

## Test Structure

- `tests/conftest.py`: Contains test fixtures (database connection, FastAPI app, async client).
- `tests/test_health.py`: Example API endpoint test.
- `tests/test_user_unit.py`: Example unit test for models.

## Database

Tests use a separate database (default: `test_db`) to avoid conflicting with development data. The database is cleaned between tests.
