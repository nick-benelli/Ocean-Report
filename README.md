# LBI-Surf: Daily Surf Wind Forecast Emailer 🌊

LBI ocean info and water temperature

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

- **Latitude**: `39.57895`
- **Longitude**: `-74.22461`
- Approximate orientation of beach: `140°` (southeast-facing)

## 🛠️ Setup

### 1. Clone the repo

```bash
git clone https://github.com/your-username/surf-wind-forecast.git
cd surf-wind-forecast
```

### 2. Add environment variables

Create a `.env` file in the root of the repo:

```ini
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_ADDRESS=your@email.com
EMAIL_PASSWORD=your_app_password
EMAIL_RECIPIENTS=friend1@example.com,friend2@example.com
EMAIL_BCC=your@email.com
```

- ✅ Use an App Password if using Gmail or another provider with 2FA.

### 🔐 3. Configure GitHub Secrets

Store the same values from your `.env` file as **GitHub Secrets** in your repository. These are used securely by the GitHub Actions workflow to send the email.

You'll need to add the following secrets:

- `EMAIL_HOST`
- `EMAIL_PORT`
- `EMAIL_ADDRESS`
- `EMAIL_PASSWORD`
- `EMAIL_RECIPIENTS`
- `EMAIL_BCC`

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

```
uv build
```

### 📂 Project Structure

```pgsql
.
├── .github/workflows/email-forecast.yml   # GitHub Actions workflow
├── forecast.py                            # Main script to fetch + email forecast
├── utils.py                               # Wind direction, conversion, formatting helpers
├── .env                                   # (Optional) Local environment variables
├── requirements.txt
└── README.md

```

### 🙏 Credits

- Open-Meteo API
- NOAA Tides & Currents
- Wind direction naming logic adapted from NWS/NOAA standards

### 🧼 License

MIT License. Use and adapt freely.

```yaml
Let me know if you'd like to include [deployment instructions](f), a [screenshots section](f), or a badge for [GitHub Actions status](f).
```
