import os
import tempfile
from lbi_surf.utils import load_config_with_env_substitution


def test_load_config_with_env_substitution(monkeypatch):
    # Set environment variables for substitution
    monkeypatch.setenv("EMAIL_SENDER", "test_sender@example.com")
    monkeypatch.setenv("EMAIL_RECIPIENT", "test_recipient@example.com")
    monkeypatch.setenv("LONGITUDE", "-74.1234")
    monkeypatch.setenv("LATITUDE", "39.5678")

    # Create a temporary config file
    config_content = """
noaa:
  station_id: "8534720"
  buoy_id: "44091"
email:
  smtp_server: "smtp.gmail.com"
  smtp_port: 587
  sender: ${EMAIL_SENDER}
  recipient: ${EMAIL_RECIPIENT}
location:
  longitude: ${LONGITUDE}
  latitude: ${LATITUDE}
"""
    with tempfile.NamedTemporaryFile("w+", delete=False) as tmp:
        tmp.write(config_content)
        tmp_path = tmp.name

    try:
        config = load_config_with_env_substitution(tmp_path)
        assert config["email"]["sender"] == "test_sender@example.com"
        assert config["email"]["recipient"] == "test_recipient@example.com"
        assert float(config["location"]["longitude"]) == -74.1234
        assert float(config["location"]["latitude"]) == 39.5678
        assert config["noaa"]["station_id"] == "8534720"
        assert config["noaa"]["buoy_id"] == "44091"
        print("test_load_config_with_env_substitution: PASS")
    finally:
        os.remove(tmp_path)
