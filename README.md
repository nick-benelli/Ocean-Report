# Ocean-Report: Daily Surf Wind Forecast Emailer 🌊

Ocean conditions, wind, and water temperature.

This project automatically fetches the wind forecast near Long Beach Island, NJ each morning and emails it to a list of recipients. It uses data from [Open-Meteo](https://open-meteo.com/) and is scheduled via GitHub Actions.

## ✨ Features

- ✅ Fetches wind speed and direction from Open-Meteo
- ✅ Converts wind data to mph and cardinal direction (e.g. NW, SE)
- ✅ Labels wind as **Offshore**, **Onshore**, or **Cross-shore** based on your beach orientation
- ✅ Formats the forecast into a clean, readable email
- ✅ Emails the forecast daily at 6:45 AM Eastern
- ✅ Only runs between **June 1** and **October 1**

## 📍 Location

The forecast is centered on:

- **Latitude**: `39.58`
- **Longitude**: `-74.22`
- Approximate orientation of beach: `140°` (southeast-facing)
- _Note: Location is approximate and can be adjusted for your local beach_

## 🛠️ Setup

### 1. Clone the repo

```bash
git clone https://github.com/your-username/ocean-report.git
cd ocean-report
```

### 2. Add environment variables

Create a `.env` file in the root of the repo (example values shown):

```ini
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_ADDRESS=your@email.com
EMAIL_PASSWORD=your_app_password
EMAIL_RECIPIENTS=recipient1@example.com,recipient2@example.com
EMAIL_BCC=your@email.com
LATITUDE=39.58
LONGITUDE=-74.22
BEACH_ORIENTATION_DEGREES=140
RECIPIENTS_GIST_URL=https://gist.github.com/your-gist-url  # optional
TEST_RECIPIENTS=your_test@email.com                        # optional
TEST_RECIPIENTS_GIST_URL=https://gist.github.com/your-test-gist-url  # optional
```

- ✅ Use an App Password if using Gmail or another provider with 2FA.
- _Do not use real email addresses in public repositories. Use environment variables or secrets for sensitive data._

### 🔐 3. Configure GitHub Secrets

Store the same values from your `.env` file as **GitHub Secrets** in your repository. These are used securely by the GitHub Actions workflow to send the email.

You'll need to add the following secrets:

- `EMAIL_HOST`
- `EMAIL_PORT`
- `EMAIL_ADDRESS`
- `EMAIL_PASSWORD`
- `EMAIL_RECIPIENTS`
- `EMAIL_BCC`
- `LATITUDE`
- `LONGITUDE`
- `BEACH_ORIENTATION_DEGREES`
- `RECIPIENTS_GIST_URL` # (optional, for dynamic recipient lists)
- `TEST_RECIPIENTS` # (optional, for testing)
- `TEST_RECIPIENTS_GIST_URL` # (optional, for testing)

> 🛡️ Go to your repo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

---

### ⏰ Schedule & Workflow

- The email is sent **daily at 6:45 AM Eastern Time** (which is **10:45 UTC**).
- The workflow **only runs between June 1 and October 1**.
- You can also **manually trigger the workflow** for testing:
  - Go to the **Actions** tab
  - Select **Daily Surf Wind Forecast**
  - Click **Run workflow**

### 📨 Email Preview

Example output:

```txt
- 8 AM: 13.0 mph from NW  (312°) → Offshore
- 12 PM:  4.0 mph from NNW (333°) → Offshore
- 3 PM: 11.9 mph from ENE ( 68°) → Cross-shore
- 6 PM:  7.5 mph from ESE (113°) → Onshore/Cross-shore

```

### 📦 Dependencies

- python 3.11
- `uv`

Install via:

```bash
uv pip install -e .
```

or

```bash
uv build
```

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
- Wind direction naming logic adapted from NWS/NOAA standards

### 🧼 License

MIT License. Use and adapt freely.

```yaml
Let me know if you'd like to include deployment instructions, a screenshots section, or a badge for GitHub Actions status.
```

### Questions

Questions? Please email Nick Benelli at [nick.benelli12@gmail.com](mailto:nick.benelli12@gmail.com)
