import requests
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

# NOAA Station ID
STATION_ID = "8534720"

# NOAA API endpoints
TIDE_URL = (
    f"https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?"
    f"product=predictions&application=chatgpt-tide-app&begin_date=latest&"
    f"end_date=latest&datum=MLLW&station={STATION_ID}&time_zone=lst_ldt&"
    f"units=english&interval=hilo&format=json"
)

TEMP_URL = (
    f"https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?"
    f"product=water_temperature&application=chatgpt-tide-app&station={STATION_ID}&"
    f"date=latest&units=english&time_zone=lst_ldt&format=json"
)

# Email config
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_SENDER = "your_email@gmail.com"
EMAIL_PASSWORD = "your_app_password"  # Use app password if using Gmail
EMAIL_RECIPIENT = "your_email@gmail.com"


def fetch_tide_data():
    response = requests.get(TIDE_URL)
    data = response.json()
    return data["predictions"]


def fetch_water_temp():
    response = requests.get(TEMP_URL)
    data = response.json()
    return data["data"][0]["v"] + " °F"


def send_email(subject, body):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECIPIENT

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)


def main():
    tides = fetch_tide_data()
    water_temp = fetch_water_temp()

    high_tides = [t for t in tides if t["type"] == "H"]
    low_tides = [t for t in tides if t["type"] == "L"]

    tide_msg = "\n".join(
        [f'{t["type"]} tide at {t["t"]} — {t["v"]} ft' for t in tides]
    )

    today = datetime.now().strftime("%B %d, %Y")
    body = (
        f"Good morning! Here’s your water report for {today}:\n\n"
        f"🌡️ Water Temperature: {water_temp}\n\n"
        f"🌊 Tide Schedule:\n{tide_msg}"
    )

    send_email(subject=f"Daily Water Report – {today}", body=body)


if __name__ == "__main__":
    main()
