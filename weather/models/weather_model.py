import logging
import os
import time
from typing import List, Tuple, Dict

from weather.models.locations_model import Locations
from weather.utils.api_utils import get_current_weather, get_forecast
from weather.utils.logger import configure_logger

logger = logging.getLogger(__name__)
configure_logger(logger)


class WeatherModel:
    """
    A class to manage user favorite locations and cached weather data.

    Provides methods to add/remove favorites, retrieve current weather and forecasts,
    with in-memory caching and TTL support.
    """

    def __init__(self):
        # List of favorite location IDs (ints)
        self.favorites: List[int] = []
        # Caches for weather and forecast data
        self._weather_cache: Dict[int, dict] = {}
        self._weather_ttl: Dict[int, float] = {}
        self._forecast_cache: Dict[Tuple[int, int], dict] = {}
        self._forecast_ttl: Dict[Tuple[int, int], float] = {}
        # TTL in seconds for cached entries
        self.ttl_seconds = int(os.getenv("TTL", 60))

    ##################################################
    # Internal Cache Management
    ##################################################

    def _get_current_weather(self, loc_id: int) -> dict:
        now = time.time()
        if loc_id in self._weather_cache and self._weather_ttl.get(loc_id, 0) > now:
            logger.debug(f"Location {loc_id} weather from cache")
            return self._weather_cache[loc_id]

        # Validate existence of location
        loc = Locations.get_location_by_id(loc_id)
        # Use city_name (or lat/lon) for API query
        city_query = loc.city_name  # assume code field matches API query
        logger.info(f"Fetching current weather for location {loc_id} ({city_code})")
        data = get_current_weather(city_query)

        self._weather_cache[loc_id] = data
        self._weather_ttl[loc_id] = now + self.ttl_seconds
        return data

    def _get_forecast(self, loc_id: int, cnt: int) -> dict:
        key = (loc_id, cnt)
        now = time.time()
        if key in self._forecast_cache and self._forecast_ttl.get(key, 0) > now:
            logger.debug(f"Location {loc_id} forecast from cache (cnt={cnt})")
            return self._forecast_cache[key]

        # Validate existence of location
        loc = Locations.get_location_by_id(loc_id)
        city_query = loc.city_name
        logger.info(f"Fetching forecast for location {loc_id} (cnt={cnt})")
        data = get_forecast(city_query, cnt=cnt)

        self._forecast_cache[key] = data
        self._forecast_ttl[key] = now + self.ttl_seconds
        return data

    ##################################################
    # Favorite Locations Management
    ##################################################

    def add_favorite(self, loc_id: int) -> None:
        """Add a new favorite location by its ID."""
        logger.info(f"Adding favorite location {loc_id}")
        loc_id = self._validate_location_id(loc_id)
        if loc_id in self.favorites:
            logger.error(f"Location {loc_id} already in favorites")
            raise ValueError(f"Location {loc_id} already a favorite")
        # Trigger validation and existence check
        _ = Locations.get_location_by_id(loc_id)
        self.favorites.append(loc_id)
        logger.info(f"Location {loc_id} added to favorites")

    def remove_favorite(self, loc_id: int) -> None:
        """Remove a favorite location by its ID."""
        logger.info(f"Removing favorite location {loc_id}")
        self._ensure_non_empty()
        loc_id = self._validate_location_id(loc_id)
        if loc_id not in self.favorites:
            logger.error(f"Location {loc_id} not in favorites")
            raise ValueError(f"Location {loc_id} not in favorites")
        self.favorites.remove(loc_id)
        logger.info(f"Location {loc_id} removed from favorites")

    def clear_favorites(self) -> None:
        """Clear all favorite locations."""
        logger.info("Clearing all favorite locations")
        self.favorites.clear()
        logger.info("All favorites cleared")

    ##################################################
    # Retrieval Functions
    ##################################################

    def get_all_favorites(self) -> List[dict]:
        """Get current weather for all favorite locations."""
        self._ensure_non_empty()
        return [self._get_current_weather(loc_id) for loc_id in self.favorites]

    def get_current_for(self, loc_id: int) -> dict:
        """Get current weather for a specific favorite location."""
        loc_id = self._validate_location_id(loc_id)
        return self._get_current_weather(loc_id)

    def get_forecast_for(self, loc_id: int, cnt: int = 5) -> dict:
        """Get forecast for a specific favorite location."""
        loc_id = self._validate_location_id(loc_id)
        return self._get_forecast(loc_id, cnt)

    ##################################################
    # Helpers
    ##################################################

    def _validate_location_id(self, loc_id: int) -> int:
        if not isinstance(loc_id, int) or loc_id < 1:
            logger.error(f"Invalid location ID: {loc_id}")
            raise ValueError(f"Invalid location ID: {loc_id}")
        return loc_id

    def _ensure_non_empty(self) -> None:
        if not self.favorites:
            logger.error("No favorite locations set")
            raise ValueError("No favorite locations set")
