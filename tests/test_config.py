import os
import tempfile
from ocean_report.config.schemas import OceanReportConfig
from ocean_report.config.loader import get_config, get_settings, load_config_with_env_substitution


def test_load_config_with_env_substitution(monkeypatch):
    # Set environment variables for substitution
    monkeypatch.setenv("EMAIL_SENDER", "test_sender@example.com")
    monkeypatch.setenv("EMAIL_RECIPIENTS", "test_recipient@example.com")
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
  recipients: ${EMAIL_RECIPIENTS}
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
        assert config["email"]["recipients"] == "test_recipient@example.com"
        assert float(config["location"]["longitude"]) == -74.1234
        assert float(config["location"]["latitude"]) == 39.5678
        assert config["noaa"]["station_id"] == "8534720"
        assert config["noaa"]["buoy_id"] == "44091"
        print("test_load_config_with_env_substitution: PASS")
    finally:
        os.remove(tmp_path)


def test_ocean_report_config_normalizes_unresolved_placeholders(monkeypatch):
    monkeypatch.delenv("MISSING_STATION_ID", raising=False)
    monkeypatch.delenv("MISSING_EMAIL_SENDER", raising=False)
    monkeypatch.delenv("MISSING_EMAIL_SMTP_PORT", raising=False)
    monkeypatch.delenv("MISSING_RECIPIENTS_GIST_URL", raising=False)
    monkeypatch.delenv("MISSING_LONGITUDE", raising=False)
    monkeypatch.delenv("MISSING_LATITUDE", raising=False)
    monkeypatch.delenv("MISSING_BEACH_ORIENTATION_DEGREES", raising=False)
    monkeypatch.delenv("MISSING_MEMORIAL_DAY_OFFSET", raising=False)
    monkeypatch.delenv("MISSING_LABOR_DAY_OFFSET", raising=False)

    config_content = """
noaa:
  station_id: "${MISSING_STATION_ID}"
email:
  sender: "${MISSING_EMAIL_SENDER}"
  smtp_port: "${MISSING_EMAIL_SMTP_PORT}"
  recipient_urls:
    main: "${MISSING_RECIPIENTS_GIST_URL}"
location:
  longitude: "${MISSING_LONGITUDE}"
  latitude: "${MISSING_LATITUDE}"
  beach_orientation_degrees: "${MISSING_BEACH_ORIENTATION_DEGREES}"
summer:
  memorial_day_offset: "${MISSING_MEMORIAL_DAY_OFFSET}"
  labor_day_offset: "${MISSING_LABOR_DAY_OFFSET}"
"""
    with tempfile.NamedTemporaryFile("w+", delete=False) as tmp:
        tmp.write(config_content)
        tmp_path = tmp.name

    try:
        raw_config = load_config_with_env_substitution(tmp_path)
        settings = OceanReportConfig.model_validate(raw_config)
        dumped_config = settings.model_dump(exclude_none=True)

        assert settings.noaa.station_id == "8534720"
        assert settings.email.sender is None
        assert settings.email.smtp_port == 587
        assert settings.email.recipient_urls.main == ""
        assert settings.location.longitude == -74.2
        assert settings.location.latitude == 39.5
        assert settings.location.beach_orientation_degrees == 140
        assert settings.summer.memorial_day_offset == -4
        assert settings.summer.labor_day_offset == 7
        assert "sender" not in dumped_config["email"]
    finally:
        os.remove(tmp_path)


def test_config_package_loader_uses_temporary_config(monkeypatch):
    config_content = """
noaa:
  station_id: "9999999"
email:
  smtp_server: "smtp.example.com"
  smtp_port: 2525
  sender: "${MISSING_LOADER_SENDER}"
  recipient_urls:
    offseason: "https://example.com/offseason.txt"
location:
  longitude: -73.999
summer:
  labor_day_offset: 10
"""

    with tempfile.NamedTemporaryFile("w+", delete=False) as tmp:
        tmp.write(config_content)
        tmp_path = tmp.name

    try:
        monkeypatch.delenv("MISSING_LOADER_SENDER", raising=False)
        settings = get_settings(tmp_path)
        dumped_config = get_config(tmp_path)

        assert settings.noaa.station_id == "9999999"
        assert settings.email.smtp_server == "smtp.example.com"
        assert settings.email.smtp_port == 2525
        assert settings.email.sender is None
        assert (
            settings.email.recipient_urls.offseason
            == "https://example.com/offseason.txt"
        )
        assert settings.location.longitude == -73.999
        assert settings.location.latitude == 39.5
        assert settings.summer.memorial_day_offset == -4
        assert settings.summer.labor_day_offset == 10
        assert dumped_config["email"]["smtp_server"] == "smtp.example.com"
        assert "sender" not in dumped_config["email"]
    finally:
        os.remove(tmp_path)


if __name__ == "__main__":
    import pytest

    pytest.main([__file__])
