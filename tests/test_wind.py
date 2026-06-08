
from ocean_report.api_client.endpoints.wind import deg_to_16_point_direction, classify_wind_relative_to_beach


def test_deg_to_16_point_direction():
    assert deg_to_16_point_direction(0) == "N"
    assert deg_to_16_point_direction(90) == "E"
    assert deg_to_16_point_direction(180) == "S"
    assert deg_to_16_point_direction(270) == "W"


def test_classify_wind_relative_to_beach():
    assert classify_wind_relative_to_beach(320, 140) == "Offshore"
    assert classify_wind_relative_to_beach(140, 140) == "Onshore"
