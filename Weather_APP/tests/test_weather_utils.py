import pytest
import requests_mock
from website.weather_utils import weekday_from_date, fetch_coordinates, fetch_weather_data

def test_weekday_from_date():
    assert weekday_from_date(25, 3, 2022) == 'Friday'

@pytest.fixture
def mock_requests():
    with requests_mock.Mocker() as m:
        yield m

def test_fetch_coordinates_success(mock_requests):
    mock_requests.get("http://api.openweathermap.org/geo/1.0/direct?q=Paris&limit=1&appid=test_api_key", json=[{"lat": 48.8566, "lon": 2.3522}])
    latitude, longitude = fetch_coordinates("Paris")
    assert latitude == 48.8566
    assert longitude == 2.3522

def test_fetch_coordinates_failure(mock_requests):
    mock_requests.get("http://api.openweathermap.org/geo/1.0/direct?q=UnknownCity&limit=1&appid=test_api_key", json=[])
    latitude, longitude = fetch_coordinates("UnknownCity")
    assert latitude is None
    assert longitude is None

def test_fetch_weather_data_success(mock_requests):
    mock_requests.get('https://api.openweathermap.org/data/2.5/weather?q=Paris&appid=test_api_key&units=metric', json={"cod": "200"})
    mock_requests.get('https://api.openweathermap.org/data/2.5/forecast?q=Paris&appid=test_api_key&units=metric', json={"cod": "200"})
    weather_response, forecast_response = fetch_weather_data("Paris")
    assert weather_response is not None
    assert forecast_response is not None

def test_fetch_weather_data_failure(mock_requests):
    mock_requests.get('https://api.openweathermap.org/data/2.5/weather?q=UnknownCity&appid=test_api_key&units=metric', json={"cod": "404"})
    mock_requests.get('https://api.openweathermap.org/data/2.5/forecast?q=UnknownCity&appid=test_api_key&units=metric', json={"cod": "404"})
    weather_response, forecast_response = fetch_weather_data("UnknownCity")
    assert weather_response is None
    assert forecast_response is None
