import logging
import os
import time
from typing import List

from weather.utils.logger import configure_logger
from weather.db import db
from weather.models.locations_model import Locations

logger = logging.getLogger(__name__)
configure_logger(logger)

class FavoritesModel:
    """
    A class to manage favorite locations.
    """

    def __init__(self):
        """Initializes the FavoritesModel with an empty list

        Favorites is a list of locations, that starts off empty.
        The TTL (Time To Live) for song caching is set to a default value from the environment variable "TTL",
        which defaults to 60 seconds if not set.

        """
        self.favorites: List[int] = [] 
        self._favorite_cache: dict[int, Locations] = {}
        self._ttl: dict[int, float] = {}
        self.ttl_seconds = int(os.getenv("TTL", 60))   # Default TTL is 60 seconds

    ##################################################
    # Favorite Location Management Functions
    ##################################################
    def _get_song_from_cache_or_db(self, location_id: int) -> Locations:
        """
        Retrieves a location by ID, using the internal cache if possible.

        This method checks whether a cached version of the location is available
        and still valid. If not, it queries the database, updates the cache, and returns the location.

        Args:
            location_id (int): The unique ID of the location to retrieve.

        Returns:
            Location: The location object corresponding to the given ID.

        Raises:
            ValueError: If the song cannot be found in the database.
        """
        now = time.time()

        if location_id in self._favorite_cache and self._ttl.get(location_id, 0) > now:
            logger.debug(f"location ID {location_id} retrieved from cache")
            return self._favorite_cache[location_id]

        try:
            favorite = Locations.get_location_by_id(location_id)
            logger.info(f"location ID {location_id} loaded from DB")
        except ValueError as e:
            logger.error(f"location ID {location_id} not found in DB: {e}")
            raise ValueError(f"location ID {location_id} not found in database") from e

        self._favorite_cache[location_id] = favorite
        self._ttl[location_id] = now + self.ttl_seconds
        return favorite
    
    def add_location_to_favoriteslist(self, location_id: int) -> None:
        """
        Adds a location to the favoriteslist by ID, using the cache or database lookup.

        Args:
            location_id (int): The ID of the location to add to the favoriteslist.

        Raises:
            ValueError: If the location ID is invalid or already exists in the favoriteslist.
        """
        logger.info(f"Received request to add location with ID {location_id} to the favoriteslist")

        # song_id =  self.validate_song_id(location_id, check_in_playlist=False)

        if location_id in self.favorites:
            logger.error(f"Location with ID {location_id} already exists in the favoriteslist")
            raise ValueError(f"Location with ID {location_id} already exists in the favoriteslist")

        try:
            location = self._get_song_from_cache_or_db(location_id)
        except ValueError as e:
            logger.error(f"Failed to add location: {e}")
            raise

        self.playlist.append(Locations.id)
        logger.info(f"Successfully added to playlist: {location.city_name}- ({location.latitude}, {location.longitude})")


    

    ##################################################
    # Utility Functions
    ##################################################


    def check_if_empty(self) -> None:
        """
        Checks if the playlist is empty and raises a ValueError if it is.

        Raises:
            ValueError: If the playlist is empty.

        """
        if not self.favorites:
            logger.error("Favorites is empty")
            raise ValueError("Favorites is empty")