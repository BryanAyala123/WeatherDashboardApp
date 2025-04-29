import logging
import os
import requests

from weather.utils.logger import configure_logger

# Base URL and API key pulled from .env
WEATHER_API_BASE_URL = os.getenv(
    "WEATHER_API_BASE_URL",
    "https://api.openweathermap.org/data/2.5"
)
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

logger = logging.getLogger(__name__)
configure_logger(logger)


def get_current_weather(city: str, units: str = "metric") -> dict:
    """
    Fetches current weather data for the given city.

    Args:
        city (str): City name (e.g. "Boston,US").
        units (str): Units of measurement. One of "standard", "metric", or "imperial".

    Returns:
        dict: JSON-decoded response from the weather API.

    Raises:
        RuntimeError: On network errors or non-200 responses.
        ValueError: If the API returns unexpected data.
    """
    if not WEATHER_API_KEY:
        raise RuntimeError("WEATHER_API_KEY is not set in environment")

    url = f"{WEATHER_API_BASE_URL}/weather"
    params = {"q": city, "appid": WEATHER_API_KEY, "units": units}

    logger.info(f"Requesting current weather for {city} → {url} with {params}")
    try:
        resp = requests.get(url, params=params, timeout=5)
        resp.raise_for_status()
    except requests.exceptions.Timeout:
        logger.error("Weather API request timed out.")
        raise RuntimeError("Weather API request timed out.")
    except requests.exceptions.RequestException as e:
        logger.error(f"Weather API request failed: {e}")
        raise RuntimeError(f"Weather API request failed: {e}")

    data = resp.json()
    if "weather" not in data or "main" not in data:
        logger.error(f"Unexpected payload from weather API: {data}")
        raise ValueError(f"Unexpected payload from weather API: {data}")

    logger.info(f"Received weather payload: {data}")
    return data


def get_forecast(city: str, cnt: int = 5, units: str = "metric") -> dict:
    """
    Fetches forecast data for the given city.

    Args:
        city (str): City name.
        cnt (int): Number of forecast entries to return (e.g. 5 for 5 days/records).
        units (str): Units of measurement.

    Returns:
        dict: JSON-decoded forecast from the weather API.

    Raises:
        RuntimeError: On network errors or non-200 responses.
        ValueError: If the API returns unexpected data.
    """
    if not WEATHER_API_KEY:
        raise RuntimeError("WEATHER_API_KEY is not set in environment")

    url = f"{WEATHER_API_BASE_URL}/forecast"
    params = {"q": city, "cnt": cnt, "appid": WEATHER_API_KEY, "units": units}

    logger.info(f"Requesting forecast for {city} → {url} with {params}")
    try:
        resp = requests.get(url, params=params, timeout=5)
        resp.raise_for_status()
    except requests.exceptions.Timeout:
        logger.error("Forecast API request timed out.")
        raise RuntimeError("Forecast API request timed out.")
    except requests.exceptions.RequestException as e:
        logger.error(f"Forecast API request failed: {e}")
        raise RuntimeError(f"Forecast API request failed: {e}")

    data = resp.json()
    if "list" not in data:
        logger.error(f"Unexpected payload from forecast API: {data}")
        raise ValueError(f"Unexpected payload from forecast API: {data}")

    logger.info(f"Received forecast payload: {data}")
    return data
