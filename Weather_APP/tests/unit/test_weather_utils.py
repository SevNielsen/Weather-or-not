import pytest
import requests_mock
from unittest.mock import patch
from website.__init222 import create_app
from website.weather_utils import weekday_from_date, fetch_coordinates, fetch_map_data, fetch_weather_data




def test_weekday_from_date():
    assert weekday_from_date(25, 3, 2022) == 'Friday'

@pytest.fixture
def app_context():
    app = create_app()
    ctx = app.app_context()
    ctx.push()
    yield app
    ctx.pop()

@pytest.fixture
def mock_requests():
    with requests_mock.Mocker() as m:
        yield m

@pytest.fixture
def mock_env():
    with patch.dict('os.environ', {'API_KEY': 'test_api_key'}):
        yield

def test_fetch_coordinates_success(mock_requests, mock_env):
    city = "Paris"
    mock_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid=test_api_key"
    mock_requests.get(mock_url, json=[{"lat": 48.8566, "lon": 2.3522}])
    latitude, longitude = fetch_coordinates(city)
    assert latitude == 48.8566
    assert longitude == 2.3522

def test_fetch_coordinates_failure(mock_requests, mock_env, app_context):
    city = "UnknownCity"
    mock_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid=test_api_key"
    mock_requests.get(mock_url, json=[])
    latitude, longitude = fetch_coordinates(city)
    assert latitude is None
    assert longitude is None

def test_fetch_map_data(mock_env):
    layer = "temp_new"
    zoom = 10
    lat = 48.8566
    lon = 2.3522
    map_url = fetch_map_data(layer, zoom, lat, lon)
    expected_url = f"https://tile.openweathermap.org/map/{layer}/{zoom}/{lat}/{lon}.png?appid=test_api_key"
    assert map_url == expected_url

def test_fetch_weather_data_success(mock_requests, mock_env):
    city = "Paris"
    weather_url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid=test_api_key&units=metric'
    forecast_url = f'https://api.openweathermap.org/data/2.5/forecast?q={city}&appid=test_api_key&units=metric'
    mock_requests.get(weather_url, json={"cod": "200", "weather": [{"main": "Clear"}]})
    mock_requests.get(forecast_url, json={"cod": "200", "list": [{"weather": [{"main": "Clouds"}]}]})
    weather_response, forecast_response = fetch_weather_data(city)
    assert weather_response is not None
    assert forecast_response is not None

def test_fetch_weather_data_failure(mock_requests, mock_env, app_context):
    city = "UnknownCity"
    weather_url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid=test_api_key&units=metric'
    forecast_url = f'https://api.openweathermap.org/data/2.5/forecast?q={city}&appid=test_api_key&units=metric'
    mock_requests.get(weather_url, json={"cod": "404"})
    mock_requests.get(forecast_url, json={"cod": "404"})
    weather_response, forecast_response = fetch_weather_data(city)
    assert weather_response is None
    assert forecast_response is None
