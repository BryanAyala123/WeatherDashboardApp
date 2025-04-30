import pytest

from weather.models.favoriteslist_model import FavoriteslistModel


@pytest.fixture
def fav_model():
    """Provide a fresh FavoriteslistModel for each test."""
    return FavoriteslistModel()


@pytest.fixture
def sample_locations():
    """Two sample (city_name, latitude, longitude) tuples."""
    return [
        ("CityA", 10.0, 20.0),
        ("CityB", 30.0, 40.0),
    ]


def test_get_locations_with_data(fav_model, sample_locations):
    """Test retrieving locations after adding them."""
    for city, lat, lon in sample_locations:
        fav_model.add_location_to_favoriteslist(city, lat, lon)

    result = fav_model.get_all_locations()
    assert result == sample_locations


def test_add_location_to_favoriteslist(fav_model, sample_locations):
    """Test adding a single location."""
    city, lat, lon = sample_locations[0]
    fav_model.add_location_to_favoriteslist(city, lat, lon)
    assert fav_model.favoriteslist == [sample_locations[0]]


def test_add_duplicate_location_raises(fav_model, sample_locations):
    """Test that adding a duplicate raises ValueError."""
    city, lat, lon = sample_locations[0]
    fav_model.add_location_to_favoriteslist(city, lat, lon)
    with pytest.raises(ValueError, match=f"Location with name {city} already exists in the favoriteslist"):
        fav_model.add_location_to_favoriteslist(city, lat, lon)


def test_remove_location(fav_model, sample_locations):
    """Test removing an existing location."""
    # Add both
    for city, lat, lon in sample_locations:
        fav_model.add_location_to_favoriteslist(city, lat, lon)

    # Remove the first one
    city, lat, lon = sample_locations[0]
    fav_model.remove_location(city, lat, lon)

    assert fav_model.favoriteslist == [sample_locations[1]]


def test_remove_invalid_location(fav_model, sample_locations):
    """Test that removing a non-added location raises ValueError."""
    # Add only the first
    city1, lat1, lon1 = sample_locations[0]
    fav_model.add_location_to_favoriteslist(city1, lat1, lon1)

    # Attempt to remove the second
    city2, lat2, lon2 = sample_locations[1]
    with pytest.raises(ValueError, match="not found in the favoriteslist"):
        fav_model.remove_location(city2, lat2, lon2)


def test_remove_nonexistent_location(fav_model):
    """Test that removing from an empty list raises ValueError."""
    with pytest.raises(ValueError, match="favoriteslist is empty"):
        fav_model.remove_location("NoCity", 0.0, 0.0)


def test_clear_favoriteslist(fav_model, sample_locations):
    """Test clearing a populated favorites list."""
    for city, lat, lon in sample_locations:
        fav_model.add_location_to_favoriteslist(city, lat, lon)

    fav_model.clear_favoriteslist()
    assert fav_model.favoriteslist == []


def test_clear_favoriteslist_empty(fav_model, caplog):
    """Test warning is logged and list stays empty when clearing an empty list."""
    caplog.set_level("WARNING", logger="weather.models.favoriteslist_model")
    fav_model.clear_favoriteslist()
    assert fav_model.favoriteslist == []
    assert "Clearing an empty favoriteslist." in caplog.text


def test_get_all_locations_empty(fav_model):
    """Test that get_all_locations on an empty list returns [] without error."""
    result = fav_model.get_all_locations()
    assert result == []
