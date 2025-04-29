import pytest
from types import SimpleNamespace

from weather.models.weather_model import WeatherModel
from weather.models.locations_model import Locations
from weather.utils.api_utils import get_current_weather, get_forecast


@pytest.fixture
def weather_model():
    """Provide a fresh WeatherModel instance for each test."""
    return WeatherModel()


@pytest.fixture
def sample_location(mocker):
    """Fixture for a sample location object."""
    loc = SimpleNamespace(id=1, city_name="TestCity,TC")
    # Patch the Locations.get_location_by_id to return our sample
    mocker.patch.object(Locations, "get_location_by_id", return_value=loc)
    return loc


##################################################
# Update Functions Test Cases
##################################################

def test_add_favorite(weather_model, sample_location):
    """Test adding a new favorite location."""
    weather_model.add_favorite(sample_location.id)
    assert weather_model.favorites == [1]


def test_add_duplicate_favorite(weather_model, sample_location):
    """Test error when adding a duplicate favorite."""
    weather_model.add_favorite(sample_location.id)
    with pytest.raises(ValueError, match="Location 1 already a favorite"):
        weather_model.add_favorite(sample_location.id)


def test_remove_favorite(weather_model, sample_location):
    """Test removing an existing favorite location."""
    weather_model.favorites = [1]
    weather_model.remove_favorite(1)
    assert weather_model.favorites == []


def test_remove_favorite_not_in_list(weather_model, sample_location):
    """Test error when removing a favorite not in list."""
    weather_model.favorites = [2]
    with pytest.raises(ValueError, match="Location 1 not in favorites"):
        weather_model.remove_favorite(1)


def test_remove_favorite_empty_list(weather_model):
    """Test error when removing from empty favorites."""
    with pytest.raises(ValueError, match="No favorite locations set"):
        weather_model.remove_favorite(1)


def test_clear_favorites(weather_model, sample_location):
    """Test clearing all favorite locations."""
    weather_model.favorites = [1, 2]
    weather_model.clear_favorites()
    assert weather_model.favorites == []


##################################################
# Get Functions Test Cases
##################################################

def test_get_current_for(weather_model, sample_location, mocker):
    """Test retrieving current weather for a favorite location."""
    # Stub internal cache fetch
    data = {"weather": [], "main": {"temp": 10}}
    mocker.patch.object(weather_model, "_get_current_weather", return_value=data)

    result = weather_model.get_current_for(1)
    assert result == data
    weather_model._get_current_weather.assert_called_once_with(1)


def test_get_forecast_for(weather_model, sample_location, mocker):
    """Test retrieving forecast for a favorite location."""
    fc_data = {"list": []}
    mocker.patch.object(weather_model, "_get_forecast", return_value=fc_data)

    result = weather_model.get_forecast_for(1, cnt=3)
    assert result == fc_data
    weather_model._get_forecast.assert_called_once_with(1, 3)


def test_get_all_favorites(weather_model, sample_location, mocker):
    """Test retrieving weather for all favorites."""
    weather_model.favorites = [1, 2]
    responses = [{}, {}]
    # side_effect for two calls
    mocker.patch.object(weather_model, "_get_current_weather", side_effect=responses)

    result = weather_model.get_all_favorites()
    assert result == responses
    assert weather_model._get_current_weather.call_count == 2


def test_get_all_favorites_empty(weather_model):
    """Test error when retrieving all favorites on empty list."""
    with pytest.raises(ValueError, match="No favorite locations set"):
        weather_model.get_all_favorites()


##################################################
# Validation Test Cases
##################################################

def test_add_invalid_location_id(weather_model):
    """Test error on adding invalid location IDs."""
    for invalid in [0, -1, "a"]:
        with pytest.raises(ValueError, match=f"Invalid location ID: {invalid}"):
            weather_model.add_favorite(invalid)


def test_get_current_for_invalid_id(weather_model):
    """Test error when getting current for invalid ID."""
    with pytest.raises(ValueError, match="Invalid location ID: -1"):
        weather_model.get_current_for(-1)


def test_get_forecast_for_invalid_id(weather_model):
    """Test error when getting forecast for invalid ID."""
    with pytest.raises(ValueError, match="Invalid location ID: 0"):
        weather_model.get_forecast_for(0)
