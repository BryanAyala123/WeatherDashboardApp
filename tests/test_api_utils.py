import pytest
import requests
from unittest.mock import Mock

import weather.utils.api_utils as api_utils
from weather.utils.api_utils import get_current_weather, get_forecast

CITY = "TestCity,TC"
UNITS = "metric"


@pytest.fixture(autouse=True)
def set_api_key(monkeypatch):
    # Ensure our code sees a known API key
    monkeypatch.setenv("WEATHER_API_KEY", "KEY")
    monkeypatch.setattr(api_utils, "WEATHER_API_KEY", "KEY")


@pytest.fixture
def mock_requests_success(monkeypatch):
    # Create a dummy response object whose .json() and .raise_for_status() we can control
    dummy_resp = Mock()
    dummy_resp.raise_for_status = Mock()
    dummy_resp.json.return_value = {}
    # Patch requests.get to return our dummy
    dummy_get = Mock(return_value=dummy_resp)
    monkeypatch.setattr(requests, "get", dummy_get)
    return dummy_resp


@pytest.fixture
def mock_requests_forecast(monkeypatch):
    dummy_resp = Mock()
    dummy_resp.raise_for_status = Mock()
    dummy_resp.json.return_value = {}
    dummy_get = Mock(return_value=dummy_resp)
    monkeypatch.setattr(requests, "get", dummy_get)
    return dummy_resp


def test_get_current_weather_success(mock_requests_success):
    payload = {"weather": [{"desc": "clear"}], "main": {"temp": 25}}
    mock_requests_success.json.return_value = payload

    result = get_current_weather(CITY)
    assert result == payload

    requests.get.assert_called_once_with(
        f"{api_utils.WEATHER_API_BASE_URL}/weather",
        params={"q": CITY, "appid": "KEY", "units": UNITS},
        timeout=5,
    )


def test_get_current_weather_request_failure(monkeypatch):
    monkeypatch.setattr(
        requests, "get", Mock(side_effect=requests.exceptions.RequestException("Oops"))
    )
    with pytest.raises(RuntimeError, match="Weather API request failed: Oops"):
        get_current_weather(CITY)


def test_get_current_weather_timeout(monkeypatch):
    monkeypatch.setattr(
        requests, "get", Mock(side_effect=requests.exceptions.Timeout)
    )
    with pytest.raises(RuntimeError, match="Weather API request timed out."):
        get_current_weather(CITY)


def test_get_current_weather_invalid_response(mock_requests_success):
    mock_requests_success.json.return_value = {}
    with pytest.raises(ValueError, match="Unexpected payload from weather API:"):
        get_current_weather(CITY)


def test_get_forecast_success(mock_requests_forecast):
    payload = {"list": [{"dt": 12345}]}
    mock_requests_forecast.json.return_value = payload

    result = get_forecast(CITY, cnt=3)
    assert result == payload

    requests.get.assert_called_once_with(
        f"{api_utils.WEATHER_API_BASE_URL}/forecast",
        params={"q": CITY, "cnt": 3, "appid": "KEY", "units": UNITS},
        timeout=5,
    )


def test_get_forecast_request_failure(monkeypatch):
    monkeypatch.setattr(
        requests, "get", Mock(side_effect=requests.exceptions.RequestException("Oops"))
    )
    with pytest.raises(RuntimeError, match="Forecast API request failed: Oops"):
        get_forecast(CITY)


def test_get_forecast_timeout(monkeypatch):
    monkeypatch.setattr(
        requests, "get", Mock(side_effect=requests.exceptions.Timeout)
    )
    with pytest.raises(RuntimeError, match="Forecast API request timed out."):
        get_forecast(CITY)


def test_get_forecast_invalid_response(mock_requests_forecast):
    mock_requests_forecast.json.return_value = {}
    with pytest.raises(ValueError, match="Unexpected payload from forecast API:"):
        get_forecast(CITY)
