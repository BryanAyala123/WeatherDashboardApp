from datetime import datetime, timedelta, timezone
import pytest

from weather.models.locations_model import Locations

@pytest.fixture
def location_london(session):
    location = Locations(
        city_name= "London",
        latitude =51.5085,
        longitude =-0.1257,
        time = datetime(2022, 9, 4, 12, 0,0),
        temp = 282.42,
        feels_like = 280,
        pressure = 1036,
        humidity = 72,
        weather_main = "Rain",
        weather_description= "light rain"
    )
    session.add(location)
    session.commit()
    return location

@pytest.fixture
def location_zocca(session):
    location = Locations(
        city_name= "Zocca",
        latitude =44.34,
        longitude =10.99,
        time = datetime(2022, 9, 4, 12, 0,0),
        temp = 294.93,
        feels_like = 294.83,
        pressure = 1018,
        humidity = 64,
        weather_main = "Clouds",
        weather_description= "overcast clouds"
    )
    session.add(location)
    session.commit()
    return location

def test_validate(location_london):
    """Test the validate method on a valid location, should return nothing"""
    location_london.validate()

def test_validate_bad_data():
    """Test the validate method on a invalid location, should raise Value Errors"""
    bad = Locations(
        city_name="",
        latitude=100000,
        longitude=203,
        time = "not date"
    )
    with pytest.raises(ValueError):
        bad.validate()


def test_get_location_by_id(location_london):
    """ Tests the get_location_by_id on a correct id"""
    loc = Locations.get_location_by_id(location_london.id)
    assert loc is not None
    assert loc.city_name=="London"


def test_get_location_by_id_not_found(app):
    """ Tests the get_location_by_id on an incorrect id """
    with pytest.raises(ValueError):
        Locations.get_location_by_id(2039102012010121)


def test_get_current_weather(app, location_zocca):
    """ Tests the get_current_weather on a valid location """
    loc= Locations.get_current_weather("Zocca", 44.34, 10.99)
    assert loc.city_name== "Zocca"
    assert loc.temp ==294.93


def test_get_current_weather_not_found(app):
    """Test error when compound key in get_current_weather method doesn't match any record"""
    with pytest.raises(ValueError):
        Locations.get_current_weather("mylittlepony", 0.0, 0.0)


def test_get_weather_history_returns_limit_3(session):
    """Test that get_weather_history_returns only most recent entries are returned."""
    base_time = datetime.now()

    for i in range(5):
        session.add(Locations(
            city_name="cityP",
            latitude=23.12,
            longitude=40.7,
            time=base_time -timedelta(hours=i),
            temp=200 - i,
            feels_like=420 + i,
            pressure=2000 +i,
            humidity=354 - i,
            weather_main="Rain",
            weather_description="light rain"
        ))
    session.commit()

    result = Locations.get_weather_history("cityP", 23.12, 40.7)

    assert isinstance(result, list)
    assert len(result) == 3
    assert result[0].time > result[1].time > result[2].time


def test_get_weather_history_invalid(app):
    """Test error when method get_weather_history_returns does not get a valid location."""
    with pytest.raises(ValueError):
        Locations.get_weather_history("oeeaeoeeeae", 12, 34)