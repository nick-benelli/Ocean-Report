from lbi_surf.wind import deg_to_compass, classify_wind_type


def test_deg_to_compass():
    assert deg_to_compass(0) == "N"
    assert deg_to_compass(90) == "E"
    assert deg_to_compass(180) == "S"
    assert deg_to_compass(270) == "W"


def test_classify_wind_type():
    assert classify_wind_type(140, 320) == "Offshore"
    assert classify_wind_type(140, 140) == "Onshore"
