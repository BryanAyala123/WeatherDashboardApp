import logging
import os
import time
from typing import List, Tuple

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
        self.favoriteslist: List[Tuple[str, float, float]] = [] 
        self._location_cache: dict[int, Locations] = {}
        self._ttl: dict[int, float] = {}
        self.ttl_seconds = int(os.getenv("TTL", 60))   # Default TTL is 60 seconds

    ##################################################
    # Location Management Functions
    ##################################################
    
    def add_location_to_favoriteslist(self, city_name: str, latitude: float, longitude: float) -> None:
        """
        Adds a location to the favoriteslist by city_name, latitude, and longitude

        Args:
            location_id (int): The ID of the location to add to the favoriteslist.

        Raises:
            ValueError: If the location ID is invalid or already exists in the favoriteslist.
        """
        logger.info(f"Received request to add location with name {city_name}, latitude {latitude}, and longitude {longitude} to the favoriteslist")


        if city_name in self.favoriteslist: # go through the list to check the name lat and long
            logger.error(f"Location with name {city_name}, latitude {latitude}, and longitude {longitude} already exists in the favoriteslist")
            raise ValueError(f"Location with name {city_name}, latitude {latitude}, and longitude {longitude} already exists in the favoriteslist")

        try:
            location = self._get_location_from_cache_or_db(location_id)
        except ValueError as e:
            logger.error(f"Failed to add location: {e}")
            raise

        self.favoriteslist.append(Tuple[city_name, latitude, longitude])
        logger.info(f"Successfully added to favoriteslist: {location.city_name}- ({location.latitude}, {location.longitude})")


    def remove_location(self, city_name: str, latitude: float, longitude: float) -> None:
        """Removes a location from the favoriteslist by its city_name, latitude, and longitude

        Args:
            city_name (str): the city name of the location
            latitude (float): the latitude of the location
            longitude (float): the longitude of the location 

        Raises:
            ValueError: If the favoriteslist is empty or the tuple (city_name, latitude, longitude) is invalid

        """
        logger.info(f"Received request to remove location with city_name {city_name}, latitude {latitude}, longitude {longitude}")

        self.check_if_empty()
        location_id = self.validate_location_id(location_id)

        if location_id not in self.favoriteslist:
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

    def check_if_empty(self) -> None:
        """
        Checks if the favoriteslist is empty and raises a ValueError if it is.

        Raises:
            ValueError: If the favoriteslist is empty.

        """
        if not self.favoriteslist:
            logger.error("favoriteslist is empty")
            raise ValueError("favoriteslist is empty")