import logging

from sqlalchemy.exc import IntegrityError, SQLAlchemyError, desc
from typing import List
from datetime import datetime

from weather.db import db
from weather.utils.logger import configure_logger

logger = logging.getLogger(__name__)
configure_logger(logger)

class Locations(db.Model):
    """Represents a location in the catalog.

    This model maps to the 'weather_data' table and stores metadata such as city_name,
    latitude, longitude, time, temp, and more. It also tracks location count.

    Used in a Flask-SQLAlchemy application for favoriteslist management,
    user interaction, and data-driven song operations.
    """

    __tablename__ = 'weather_data'

    id = db.Column(db.Integer, primary_key=True)
    city_name= db.Column(db.String, nullable=False) 
    latitude =db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    time = db.Column(db.DateTime, nullable = False)
    temp = db.Column(db.Float)
    feels_like = db.Column(db.Float)
    pressure = db.Column(db.Integer)
    humidity = db.Column(db.Integer)
    weather_main = db.Column(db.String)
    weather_description= db.Column(db.String)

    def validate(self) -> None:
        """Validates the location instance before committing to the database.

        Raises:
            ValueError: If any required fields are invalid.
        """
        if not self.city_name or not isinstance(self.city_name, str):
            raise ValueError("City Name must be a non-empty string.")
        if not isinstance(self.latitude, float) or not(-90 <= self.latitude <= 90):
            raise ValueError("Latitude must be within bounds of [-90,90]")
        if not isinstance(self.longitude, float) or not (-180 <= self.longitude <= 180):
            raise ValueError("Latitude must be within bounds of [-180,180]")
        if not self.time or not isinstance(self.time, datetime):
            raise ValueError("Time must be in year month date ")
        
    @classmethod
    def get_location_by_id(cls, location_id:int)-> "Locations":
        """
        Retrieves a snapshot of the weather in a location from the catalog by its ID.

        Args:
            location_id (int): The ID of the location to retrieve.

        Returns:
            Locations: The location instance corresponding to the ID.

        Raises:
            ValueError: If no location with the given ID is found.
            SQLAlchemyError: If a database error occurs.
        """

        logger.info(f"Attempting to retrieve location and weather with ID {location_id}")
        try:
            location=cls.query.get(location_id)
            if not location:
                logger.info(f"Location with ID {location_id} not found")
                raise ValueError(f"Location with ID {location_id} not found")
            logger.info(f"Successfully retrieved location: {location.city_name}- ({location.latitude},{location.longitude})")
            return location 
        except SQLAlchemyError as e:
            logger.error(f"Database error while retrieving location by ID {location_id}: {e}")
            raise
    @classmethod
    def get_location_by_compound_key(cls, city_name:str,latitude: float, longitude:float) -> "Locations":
        """
        Retrieves a snapshot of the weather in a location from the catalog by its compound key (city_name, latitude, longitude).

        Args:
            city_name (str): The city name of the location.
            latitude (float): The latitude of the location.
            longitude (float): The longitude of the location.

        Returns:
            Locations: The location instance matching the provided compound key.

        Raises:
            ValueError: If no matching location is found.
            SQLAlchemyError: If a database error occurs.
        """

        logger.info(f"Attempting to retrieve location and weather with city name '{city_name}, latitude {latitude}, and longitude {longitude}")
        try:
            location=cls.query.filter_by(city_name=city_name.strip(), latitude=latitude, longitude=longitude).first()
            if not location:
                logger.info(f"Location with city name '{city_name}, latitude {latitude}, and longitude {longitude} not found")
                raise ValueError(f"Location with city name '{city_name}, latitude {latitude}, and longitude {longitude} not found")
            logger.info(f"Successfully retrieved location: {city_name}- ({latitude},{longitude})")
            return location 
        except SQLAlchemyError as e:
            logger.error(f"Database error while retrieving location by compound key"
                         f"cityname '{city_name}', latitude {latitude}, longitude {longitude}: {e}")
            raise

    @classmethod
    def get_current_weather(cls, city_name:str, latitude: float, longitude:float) -> "Locations":
        """
        Retrieves a the current latest weather in a location from the catalog by its compound key (city_name, latitude, longitude).

        Args:
            city_name (str): The city name of the location.
            latitude (float): The latitude of the location.
            longitude (float): The longitude of the location.

        Returns:
            Locations: The location instance matching the provided compound key.

        Raises:
            ValueError: If no matching location is found.
            SQLAlchemyError: If a database error occurs.
        """

        logger.info(f"Attempting to retrieve current location and weather with city name '{city_name}, latitude {latitude}, and longitude {longitude}")
        try:
            location=cls.query.filter_by(city_name=city_name.strip(), latitude=latitude, longitude=longitude).order_by(desc(cls.time)).first()
            if not location:
                logger.info(f"Location with city name '{city_name}, latitude {latitude}, and longitude {longitude} not found")
                raise ValueError(f"Location with city name '{city_name}, latitude {latitude}, and longitude {longitude} not found")
            logger.info(f"Successfully retrieved location: {city_name}- ({latitude},{longitude} at time: {location.time})")
            return location 
        except SQLAlchemyError as e:
            logger.error(f"Database error while retrieving location by compound key"
                         f"cityname '{city_name}', latitude {latitude}, longitude {longitude}: {e}")
            raise        
    
    @classmethod
    def get_weather_history(cls, city_name: str, latitude: float, longitude:float) -> List["Locations"]:
        """
        Retrieves the previous weather in a location from the catalog by its compound key (city_name, latitude, longitude).

        Args:
            city_name (str): The city name of the location.
            latitude (float): The latitude of the location.
            longitude (float): The longitude of the location.

        Returns:
            Locations: The recent 3 location instance matching the provided compound key.

        Raises:
            ValueError: If no matching location is found.
            SQLAlchemyError: If a database error occurs.
        """
        logger.info(f"Attempting to retrieve previous weather with city name '{city_name}, latitude {latitude}, and longitude {longitude}")
        try:
            location=cls.query.filter_by(city_name=city_name.strip(), latitude=latitude, longitude=longitude).order_by(desc(cls.time)).limit(3).all()
            if not location:
                logger.info(f"Location with city name '{city_name}, latitude {latitude}, and longitude {longitude} not found")
                raise ValueError(f"Location with city name '{city_name}, latitude {latitude}, and longitude {longitude} not found")
            logger.info(f"Successfully retrieved location: {location.city_name}- ({location.latitude},{location.longitude} at time: {location.time})")
            return location 
        except SQLAlchemyError as e:
            logger.error(f"Database error while retrieving location by compound key"
                         f"cityname '{city_name}', latitude {latitude}, longitude {longitude}: {e}")
            raise