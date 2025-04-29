import pytest
import requests

import weather.utils.api_utils as au
from weather.utils.api_utils import get_current_weather, get_forecast

CITY = "TestCity,TC"


@pytest.fixture(autouse=True)
def set_api_key(mocker):
    # Stub out the module‐level key to a known literal
    mocker.patch.object(au, "WEATHER_API_KEY", "KEY")


@pytest.fixture
def mock_requests_success(mocker):
    resp = mocker.Mock()
    resp.raise_for_status = mocker.Mock()
    mocker.patch("requests.get", return_value=resp)
    return resp


# ─── get_current_weather

def test_get_current_weather_success(mock_requests_success):
    mock_requests_success.json.return_value = {"weather":[{"desc":"clear"}],"main":{"temp":25}}

    result = get_current_weather(CITY)
    assert result == {"weather":[{"desc":"clear"}],"main":{"temp":25}}

    requests.get.assert_called_once_with(
        f"{au.WEATHER_API_BASE_URL}/weather",
        params={"q": CITY, "appid": "KEY", "units": "metric"},
        timeout=5,
    )


def test_get_current_weather_request_failure(mocker):
    mocker.patch(
        "requests.get",
        side_effect=requests.exceptions.RequestException("Oops")
    )
    with pytest.raises(RuntimeError, match="Weather API request failed: Oops"):
        get_current_weather(CITY)


def test_get_current_weather_timeout(mocker):
    mocker.patch("requests.get", side_effect=requests.exceptions.Timeout)
    with pytest.raises(RuntimeError, match="Weather API request timed out."):
        get_current_weather(CITY)


def test_get_current_weather_invalid_response(mock_requests_success):
    mock_requests_success.json.return_value = {}
    with pytest.raises(ValueError, match="Unexpected payload from weather API:"):
        get_current_weather(CITY)


# get_forecast 

@pytest.fixture
def mock_requests_forecast(mocker):
    resp = mocker.Mock()
    resp.raise_for_status = mocker.Mock()
    mocker.patch("requests.get", return_value=resp)
    return resp


def test_get_forecast_success(mock_requests_forecast):
    mock_requests_forecast.json.return_value = {"list":[{"dt":12345}]}

    result = get_forecast(CITY, cnt=3)
    assert result == {"list":[{"dt":12345}]}

    requests.get.assert_called_once_with(
        f"{au.WEATHER_API_BASE_URL}/forecast",
        params={"q": CITY, "cnt": 3, "appid": "KEY", "units": "metric"},
        timeout=5,
    )


def test_get_forecast_request_failure(mocker):
    mocker.patch(
        "requests.get",
        side_effect=requests.exceptions.RequestException("Oops")
    )
    with pytest.raises(RuntimeError, match="Forecast API request failed: Oops"):
        get_forecast(CITY)


def test_get_forecast_timeout(mocker):
    mocker.patch("requests.get", side_effect=requests.exceptions.Timeout)
    with pytest.raises(RuntimeError, match="Forecast API request timed out."):
        get_forecast(CITY)


def test_get_forecast_invalid_response(mock_requests_forecast):
    mock_requests_forecast.json.return_value = {}
    with pytest.raises(ValueError, match="Unexpected payload from forecast API:"):
        get_forecast(CITY)
