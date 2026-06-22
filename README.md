# Ocean-Report: Daily Surf Wind Forecast Emailer 🌊

[![GitHub Actions Status](https://github.com/nick-benelli/ocean-report/actions/workflows/daily-water-report.yml/badge.svg)](https://github.com/nick-benelli/ocean-report/actions)

Automated daily surf, wind, and water temperature forecast originally designed for Long Beach Island, NJ.  
This tool can be adapted to any coastal location by updating the following parameters:

- **Longitude**
- **Latitude**
- **NOAA Station ID**
- **Beach Orientation (in degrees — the direction the beach faces, e.g. 140° for southeast-facing beaches)**

This project fetches the wind forecast each morning and emails it to a list of recipients. It uses [NOAA](https://tidesandcurrents.noaa.gov/) for water and [Open-Meteo](https://open-meteo.com/) wind data and is scheduled via GitHub Actions.

## ✨ Features

- Fetches wind speed and direction from Open-Meteo
- Converts wind data to mph and cardinal direction (e.g. NW, SE)
- Labels wind as **Offshore**, **Onshore**, or **Cross-shore** based on beach orientation
- Formats the forecast into a clean, readable email
- Emails the forecast daily at 6:45 AM Eastern

## 📍 Location

- **Latitude**: `39.58`
- **Longitude**: `-74.22`
- **Beach orientation**: `140°` (southeast-facing)
- _Location is approximate and can be adjusted for your local beach_

## 🛠️ Setup

### 1. Clone the repository

```bash
git clone https://github.com/nick-benelli/ocean-report.git
cd ocean-report
```

### 2. Install dependencies

**For development (editable install - recommended):**

```bash
uv pip install -e .
```

**For production/deployment (locked dependencies):**

```bash
uv sync
```

> **Note:** Editable install means code changes take effect immediately without reinstalling.

### 3. Configure environment variables

Create a `.env` file in the root directory (copy from `.env.template`). Example:

```ini
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_ADDRESS=your@email.com
EMAIL_PASSWORD=your_app_password
EMAIL_RECIPIENTS=recipient1@example.com,recipient2@example.com
EMAIL_BCC=recipient1@example.com
LATITUDE=39.58
LONGITUDE=-74.22
BEACH_ORIENTATION_DEGREES=140
RECIPIENTS_GIST_URL=https://gist.github.com/your-gist-url  # optional
TEST_RECIPIENTS=your_test@email.com                        # optional
TEST_RECIPIENTS_GIST_URL=https://gist.github.com/your-test-gist-url  # optional
```

- Use an App Password if your email provider requires 2FA.
- **Never commit real credentials to public repositories.**

**See also:** [Configuration Setup Guide](docs/guides/config-setup.md) for advanced configuration options, Docker deployment, and multi-environment setup.

### 4. Add GitHub Secrets

Store the same values from your `.env` file as **GitHub Secrets** for use in Actions workflows.

Required secrets:

- `EMAIL_HOST`
- `EMAIL_PORT`
- `EMAIL_ADDRESS`
- `EMAIL_PASSWORD`
- `EMAIL_RECIPIENTS`
- `EMAIL_BCC`
- `LATITUDE`
- `LONGITUDE`
- `BEACH_ORIENTATION_DEGREES`

Optional/test secrets:

- `RECIPIENTS_GIST_URL`
- `TEST_RECIPIENTS`
- `TEST_RECIPIENTS_GIST_URL`

> Go to **Settings → Secrets and variables → Actions → New repository secret**

---

### ⏰ Schedule & Workflow

- **Daily at 6:45 AM Eastern Time** (10:45 UTC)
- Runs only between **June 1 - October 1** (inclusive, summer season)
- **Manual run:** Actions tab → Daily Surf Wind Forecast → Run workflow

### 📨 Email Preview

Example output:

```txt
🌊 Daily Ocean Report - Long Beach Island, NJ
📅 June 17, 2026

🌡️ Water Temperature: 68.5°F

💨 Wind Forecast:
- 8 AM:  13.0 mph from NW  (312°) → Offshore
- 12 PM:  4.0 mph from NNW (333°) → Offshore  
- 3 PM:  11.9 mph from ENE ( 68°) → Cross-shore
- 6 PM:   7.5 mph from ESE (113°) → Onshore/Cross-shore
```

### 📦 Dependencies

- Python 3.12+
- [`uv`](https://github.com/astral-sh/uv) (fast Python package installer)

**Install `uv` first (if not already installed):**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
# or on macOS:
brew install uv
```

**Then install the project:**

```bash
# Development mode (recommended - code changes take effect immediately):
uv pip install -e .

# Production mode (uses locked dependencies from uv.lock):
uv sync
```

### 🚀 Running the Project

**Send email (production):**

```bash
uv run scripts/run_report.py
```

**Preview without sending (testing):**

```bash
uv run scripts/run_report_no_email.py
```

**Jupyter Notebook:**

Open `notebooks/run.ipynb` and run the cells.

**See also:** [Email Preview Guide](docs/guides/email-preview.md) for testing workflows

### 📚 Documentation

**Comprehensive documentation is available in the [`docs/`](docs/) folder:**

- **[Documentation Hub](docs/README.md)** - Start here! Complete overview and navigation guide
- **[Architecture Documentation](docs/architecture/README.md)** - Technical deep dive into system design and components
- **[Practical Guides](docs/guides/README.md)** - How-to guides for configuration, logging, testing, and deployment

**Quick Links:**
- [Configuration Setup Guide](docs/guides/config-setup.md) - Environment setup and deployment
- [Logging Guide](docs/guides/logging.md) - Configure logging for different environments
- [Email Preview System](docs/guides/email-preview.md) - Test emails before sending
- [System Architecture Overview](docs/architecture/README.md) - Understand how components fit together

### 📂 Project Structure

```
.
├── configs/                 # YAML configuration files
├── docs/                    # Comprehensive documentation
│   ├── architecture/        # Technical component docs
│   └── guides/              # Practical how-to guides
├── help/bin/                # Helper shell scripts
├── logs/                    # Log output (gitignored)
├── notebooks/               # Jupyter notebooks for development
├── scripts/                 # Executable Python scripts
├── src/ocean_report/        # Main application code
│   ├── api_client/          # HTTP client with retry logic
│   ├── application/         # Dependency injection container
│   ├── config/              # Configuration loading
│   ├── emailer/             # Email formatting and delivery
│   ├── endpoints/           # API endpoint implementations (NOAA, Open-Meteo, NDBC)
│   ├── models/              # Pydantic data models
│   ├── services/            # Data fetching services
│   ├── use_cases/           # Business logic layer
│   ├── utils/               # Utility functions
│   ├── workflows/           # Top-level orchestration
│   └── logger.py            # Logging configuration
├── tests/                   # Unit and integration tests
└── pyproject.toml           # Project metadata and dependencies
```

**See also:** [System Architecture Overview](docs/architecture/README.md) for detailed component documentation

---

## 🙏 Credits

- [Open-Meteo API](https://open-meteo.com/) - Wind forecast data
- [NOAA Tides & Currents](https://tidesandcurrents.noaa.gov/) - Water temperature data
- Wind direction logic adapted from NWS/NOAA standards

## 📄 License

[Non-Commercial License (Modified MIT)](LICENSE)

Copyright © 2025 Nick Benelli. This software may be used for personal and non-commercial purposes only.

## 📧 Contact

Questions or feedback? Email Nick Benelli at [nick.benelli12@gmail.com](mailto:nick.benelli12@gmail.com)
