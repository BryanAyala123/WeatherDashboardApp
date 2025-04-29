import logging
import os
import time
from typing import List

from weather.utils.logger import configure_logger
from weather.db import db
from weather.models.locations_model import Locations

logger = logging.getLogger(__name__)
configure_logger(logger)

class FavoriteslistModel:
    """
    A class to manage favorite locations.
    """

    def __init__(self):
        """Initializes the FavoritesModel with an empty list

        Favorites is a list of locations, that starts off empty.
        The TTL (Time To Live) for location caching is set to a default value from the environment variable "TTL",
        which defaults to 60 seconds if not set.

        """
        self.favoriteslist: List[int] = [] 
        self._location_cache: dict[int, Locations] = {}
        self._ttl: dict[int, float] = {}
        self.ttl_seconds = int(os.getenv("TTL", 60))   # Default TTL is 60 seconds

    ##################################################
    # Location Management Functions
    ##################################################
    def _get_location_from_cache_or_db(self, location_id: int) -> Locations:
        """
        Retrieves a location by ID, using the internal cache if possible.

        This method checks whether a cached version of the location is available
        and still valid. If not, it queries the database, updates the cache, and returns the location.

        Args:
            location_id (int): The unique ID of the location to retrieve.

        Returns:
            Location: The location object corresponding to the given ID.

        Raises:
            ValueError: If the location cannot be found in the database.
        """
        now = time.time()

        if location_id in self._location_cache and self._ttl.get(location_id, 0) > now:
            logger.debug(f"location ID {location_id} retrieved from cache")
            return self._location_cache[location_id]

        try:
            location = Locations.get_location_by_id(location_id)
            logger.info(f"location ID {location_id} loaded from DB")
        except ValueError as e:
            logger.error(f"location ID {location_id} not found in DB: {e}")
            raise ValueError(f"location ID {location_id} not found in database") from e

        self._location_cache[location_id] = location
        self._ttl[location_id] = now + self.ttl_seconds
        return location
    
    def add_location_to_favoriteslist(self, location_id: int) -> None:
        """
        Adds a location to the favoriteslist by ID, using the cache or database lookup.

        Args:
            location_id (int): The ID of the location to add to the favoriteslist.

        Raises:
            ValueError: If the location ID is invalid or already exists in the favoriteslist.
        """
        logger.info(f"Received request to add location with ID {location_id} to the favoriteslist")


        if location_id in self.favorites:
            logger.error(f"Location with ID {location_id} already exists in the favoriteslist")
            raise ValueError(f"Location with ID {location_id} already exists in the favoriteslist")

        try:
            location = self._get_location_from_cache_or_db(location_id)
        except ValueError as e:
            logger.error(f"Failed to add location: {e}")
            raise

        self.favoriteslist.append(Locations.id)
        logger.info(f"Successfully added to favoriteslist: {location.city_name}- ({location.latitude}, {location.longitude})")

    def remove_location_by_location_id(self, location_id: int) -> None:
        """Removes a location from the favoriteslist by its location ID.

        Args:
            location_id (int): The ID of the location to remove from the favoriteslist.

        Raises:
            ValueError: If the favoriteslist is empty or the location ID is invalid.

        """
        logger.info(f"Received request to remove location with ID {location_id}")

        self.check_if_empty()
        location_id = self.validate_location_id(location_id)

        if location_id not in self.favorites:
            logger.warning(f"location with ID {location_id} not found in the favoriteslist")
            raise ValueError(f"location with ID {location_id} not found in the favoriteslist")

        self.favoriteslist.remove(location_id)
        logger.info(f"Successfully removed location with ID {location_id} from the favoriteslist")

    def clear_favoriteslist(self) -> None:
        """Clears all locations from the favoriteslist.

        Clears all locations from the favoriteslist. If the favoriteslist is already empty, logs a warning.

        """
        logger.info("Received request to clear the favoriteslist")

        try:
            if self.check_if_empty():
                pass
        except ValueError:
            logger.warning("Clearing an empty favoriteslist")

        self.favoriteslist.clear()
        logger.info("Successfully cleared the favoriteslist")


    ##################################################
    # favoriteslist Retrieval Functions
    ##################################################

    def get_all_locations(self) -> List[Locations]:
        """Returns a list of all location in the favorites using cached location data.

        Returns:
            List[Location]: A list of all locations in the favorites list .

        Raises:
            ValueError: If the favorites is empty.
        """
        self.check_if_empty()
        logger.info("Retrieving all locations in favoriteslist")
        return [self._get_location_from_cache_or_db(location_id) for location_id in self.favoriteslist]


    ##################################################
    # Utility Functions
    ##################################################
    def validate_location_id(self, location_id: int, check_in_favoriteslist: bool = True) -> int:
        """
        Validates the given location ID.

        Args:
            location_id (int): The location ID to validate.
            check_in_favoriteslist (bool, optional): If True, verifies the ID is present in the favoriteslist.
                                                If False, skips that check. Defaults to True.

        Returns:
            int: The validated location ID.

        Raises:
            ValueError: If the location ID is not a non-negative integer,
                        not found in the favoriteslist (if favoriteslist=True),
                        or not found in the database.
        """
        try:
            location_id = int(location_id)
            if location_id < 0:
                raise ValueError
        except ValueError:
            logger.error(f"Invalid location id: {location_id}")
            raise ValueError(f"Invalid location id: {location_id}")

        if check_in_favoriteslist and location_id not in self.playlist:
            logger.error(f"location with id {location_id} not found in favoriteslist")
            raise ValueError(f"location with id {location_id} not found in favoriteslist")

        try:
            self._get_location_from_cache_or_db(location_id)
        except Exception as e:
            logger.error(f"location with id {location_id} not found in database: {e}")
            raise ValueError(f"location with id {location_id} not found in database")

        return location_id

    def check_if_empty(self) -> None:
        """
        Checks if the favoriteslist is empty and raises a ValueError if it is.

        Raises:
            ValueError: If the favoriteslist is empty.

        """
        if not self.favoriteslist:
            logger.error("favoriteslist is empty")
            raise ValueError("favoriteslist is empty")