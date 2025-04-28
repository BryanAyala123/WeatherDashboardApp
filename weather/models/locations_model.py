from weather.db import db
# from weather.utils.logger import configure_logger
# from weather.utils.api_utils import get_random

class Locations(db.Model):
    """Represents the weather data for a location 
    """
    __tablename__ = 'weather_data'

    id = db.Column(db.Integer, primary_key=True)
    city_name= db.Column(db.String, nullable=False) 
    latitude =db.Column(db.Double, nullable=False)
    longitude = db.Column(db.Double, nullable=False)
    time = db.Column(db.DateTime, nullable = False)
    temp = db.Column(db.float)
    feels_like = db.Column(db.Float)
    pressure = db.Column(db.Integer)
    humidity = db.Column(db.Integer)
    weather_main = db.Column(db.String)
    weather_description= db.Column(db.String)

    #vvalidate_location_id

    # @classmethod
    # def get_location_by_id