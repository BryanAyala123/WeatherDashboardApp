from datetime import datetime  
import pytest

from weather.models.favoriteslist_model import FavoriteslistModel
from weather.models.locations_model import Locations

@pytest.fixture
def fav_model():
    """Fixture to provide a new instance of FavoriteslistModel for each test
    
    """
    return FavoriteslistModel()

def sample_location1(session):
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

def sample_location2(session):
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

@pytest.fixture
def sample_locations(sample_location1, sample_location2):
    return [sample_location1, sample_location2]


def test_clear_favoriteslist(fav_model):
    """Test that clear_favoriteslist empties the list.

    """
    fav_model.favoriteslist = [("example1", 10, -10), ("example2", 20, -10)]  # Assuming Locations example1 and example2 are in the list

    fav_model.clear_favoriteslist()

    assert len(fav_model.favoriteslist) == 0, "favoriteslist should be empty after calling clear_favoriteslist."

def test_clear_favoriteslist_empty(fav_model, caplog):
    """Test that calling clear_favoriteslist on an empty list logs a warning and keeps the list empty.

    """
    with caplog.at_level("WARNING"):
        fav_model.clear_favoriteslist()

    assert len(fav_model.favoriteslist) == 0, "list should remain empty if it was already empty."

    assert "Clearing an empty favoriteslist." in caplog.text

def test_get_locations_empty(fav_model, caplog):
    """Test that get_all_locations returns an empty list when there are no locations and logs a warning.
    
    """
    with caplog.at_level("WARNING"):
        locations = fav_model.get_all_locations()

    assert locations == [], "Expected get_all_locations to return an empty list when there are no locations."

    assert "Retrieving locations from an empty favoriteslist." in caplog.text


def test_get_locations_with_data(app, fav_model, sample_locations):
    """Test that get_all_locations returns the correct list when there are locations.

    # Note that app is a fixture defined in the conftest.py file

    """
    fav_model.favoriteslist.extend([(location.city_name,location.latitude, location.longitude) for location in sample_locations])

    locations = fav_model.get_all_locations()
    assert locations == sample_locations, "Expected get_all_locations to return the correct locations list."


def test_add_location_to_favoriteslist(fav_model, sample_locations, app):
    """Test that a location is correctly added to the favoriteslist.

    """
    fav_model.add_location_to_favoriteslist(sample_locations[0].city_name, sample_locations[0].latitude,sample_locations[0].longitude)  
    # Assuming location is "London"

    assert len(fav_model.favoriteslist) == 1, "favoriteslist should contain one location after calling add_location_to_favoriteslist."
    assert fav_model.favoriteslist[0] == ("London",51.5085, -0.1257), "Expected ('London',51.5085, -0.1257) in the list."

    fav_model.add_location_to_favoriteslist(sample_locations[1].city_name, sample_locations[1].latitude,sample_locations[1].longitude)  # Assuming location is Zocca 
    assert len(fav_model.favoriteslist) == 2, "favoriteslist should contain two locations after calling add_location_to_favoriteslist."
    assert fav_model.favoriteslist[1] == ("Zocca",44.34, 10.99), "Expected ('Zocca',44.34, 10.99) in the list."


def test_add_duplicate_location_raises(fav_model, sample_locations, app):
    """Test that the add_location_to_favoriteslist method raises a ValueError when attempting to add an already existing location to favoriteslist.

    """
    fav_model.add_location_to_favoriteslist(sample_locations[0].city_name, sample_locations[0].latitude,sample_locations[0].longitude)  

    with pytest.raises(ValueError):
        fav_model.add_location_to_favoriteslist(sample_locations[0].city_name, sample_locations[0].latitude,sample_locations[0].longitude)


def test_remove_location(fav_model, sample_locations, app):
    """Test that a location is correctly removed from the favoriteslist.

    """
    fav_model.add_location_to_favoriteslist(sample_locations[0].city_name, sample_locations[0].latitude,sample_locations[0].longitude)  

    fav_model.remove_location(sample_locations[0].city_name, sample_locations[0].latitude,sample_locations[0].longitude)
    assert len(fav_model.favoriteslist) == 0, "favoriteslist should contain 0 locations after remove_location."


def test_remove_invalid_location(fav_model, sample_locations, app):
    """Test that the remove_location method raises a ValueError when there's no locations.

    """
    with pytest.raises(ValueError):
        fav_model.remove_location(sample_locations[0].city_name, sample_locations[0].latitude,sample_locations[0].longitude)


def test_remove_nonexistent_location(fav_model, sample_locations, app):
    """Test that the remove_location method raises a ValueError when attempting to remove a location not on the favoriteslist.

    """
    fav_model.add_location_to_favoriteslist(sample_locations[0].city_name, sample_locations[0].latitude,sample_locations[0].longitude)
    with pytest.raises(ValueError):
        fav_model.remove_location(sample_locations[1].city_name, sample_locations[1].latitude,sample_locations[1].longitude)

