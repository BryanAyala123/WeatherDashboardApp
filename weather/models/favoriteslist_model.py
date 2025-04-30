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

        """
        self.favoriteslist: List[Tuple[str, float, float]] = [] 

    ##################################################
    # Location Management Functions
    ##################################################
    
    def add_location_to_favoriteslist(self, city_name: str, latitude: float, longitude: float) -> None:
        """
        Adds a location to the favoriteslist by city_name, latitude, and longitude

        Args:
            city_name (str): the city name of the location
            latitude (float): the latitude of the location
            longitude (float): the longitude of the location 

        Raises:
            ValueError: If the combination of city_name, latitude, and longitude already exists in favoriteslist
        """
        logger.info(f"Received request to add location with name {city_name}, latitude {latitude}, and longitude {longitude} to the favoriteslist")
        tuple_input = (city_name.strip(), latitude, longitude)

        if tuple_input in self.favoriteslist: # go through the list to check the name lat and long
            logger.error(f"Location with name {city_name} already exists in the favoriteslist")
            raise ValueError(f"Location with name {city_name} already exists in the favoriteslist")

        self.favoriteslist.append(tuple_input)
        logger.info(f"Successfully added to favoriteslist: {tuple_input}")


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
        tuple_input = (city_name.strip(), latitude, longitude)
        if tuple_input not in self.favoriteslist:
            logger.warning(f"Location with {tuple_input} not found in the favoriteslist")
            raise ValueError(f"Location with name {tuple_input} not found in the favoriteslist")

        self.favoriteslist.remove(tuple_input)
        logger.info(f"Successfully removed location {tuple_input} from the favoriteslist")

    def clear_favoriteslist(self) -> None:
        """Clears all locations from the favoriteslist.

        Clears all locations from the favoriteslist. If the favoriteslist is already empty, logs a warning.

        """
        logger.info("Received request to clear the favoriteslist")

        if not self.favoriteslist:
            logger.warning("Clearing an empty favoriteslist.")
            return

        self.favoriteslist.clear()
        logger.info("Successfully cleared the favoriteslist")


    ##################################################
    # favoriteslist Retrieval Functions
    ##################################################

    def get_all_locations(self) -> List[Tuple[str,float,float]]:
        """Returns a list of all location in the favorites using cached location data.

        Returns:
            List[Tuple[str,float,float]]: A list of all locations name, latitude, and longitude in the favorites list .
        """     
        if not self.favoriteslist:
            logger.warning("Retrieving locations from an empty favoriteslist.")
            return []

        logger.info("Retrieving all locations in favoriteslist")
        return self.favoriteslist

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