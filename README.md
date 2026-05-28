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
git clone https://github.com/your-username/ocean-report.git
cd ocean-report
```

### 2. Configure environment variables

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

### 3. Add GitHub Secrets

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
- Runs only between **June 1 and October 1**
- **Manual run:** Actions tab → Daily Surf Wind Forecast → Run workflow

### 📨 Email Preview

Example output:

```txt
- 8 AM: 13.0 mph from NW  (312°) → Offshore
- 12 PM:  4.0 mph from NNW (333°) → Offshore
- 3 PM: 11.9 mph from ENE ( 68°) → Cross-shore
- 6 PM:  7.5 mph from ESE (113°) → Onshore/Cross-shore
```

### 📦 Dependencies

- Python 3.11+
- [`uv`](https://github.com/astral-sh/uv) (fast Python package installer)

Install dependencies:

```bash
uv pip install -e .
```

### 🚀 Running the Project

**Command line:**

```bash
uv run scripts/run-report.py
```

**Jupyter Notebook:**

Open `notebooks/run.ipynb` and run the cells.

### 🧭 Documentation

- [Architecture](resources/docs/architecture.md)

### 📂 Project Structure

```pgsql
.
├── LICENSE
├── README.md
├── bash-commands
│   └── run-package.sh
├── config.yaml
├── main.py
├── notebooks
│   ├── README.md
│   ├── run.ipynb
├── pyproject.toml
├── src
│   └── ocean_report
│       ├── __init__.py
│       ├── address_fetcher.py
│       ├── config.py
│       ├── constants.py
│       ├── email_formatter.py
│       ├── emailer.py
│       ├── logger.py
│       ├── main.py
│       ├── tide.py
│       ├── utils.py
│       ├── water_temp.py
│       └── wind.py
├── tests
│   ├── test_config.py
│   ├── test_email_formatter.py
│   ├── test_gist_url.py
│   ├── test_noaa_data.py
│   ├── test_open_meto.py
│   └── test_wind.py
└── uv.lock
```

### 🙏 Credits

- Open-Meteo API
- NOAA Tides & Currents
- Wind direction logic adapted from NWS/NOAA standards

### 🧼 License

Non-Commercial License (Modified MIT)

---

Let me know if you'd like to add deployment instructions, screenshots, or additional badges.

### Questions

Questions? Email Nick Benelli: [nick.benelli12@gmail.com](mailto:nick.benelli12@gmail.com)
