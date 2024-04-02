import pytest
import requests_mock
from website.weather_utils import get_weather

@pytest.fixture
def mock_requests():
    with requests_mock.Mocker() as m:
        yield m

def test_get_weather_success(mock_requests):
    city = "London"
    mock_response = {
        "weather": [{
            "main": "Clouds",
            "description": "overcast clouds"
        }],
        "main": {
            "temp": 286.67
        }
    }
    api_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid=your_api_key"
    mock_requests.get(api_url, json=mock_response)

    weather = get_weather(city)
    assert weather is not None
    assert weather['main'] == "Clouds"
    assert weather['description'] == "overcast clouds"
    assert weather['temp'] == 286.67

def test_get_weather_failure(mock_requests):
    city = "InvalidCity"
    api_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid=your_api_key"
    mock_requests.get(api_url, status_code=404, json={"cod": "404", "message": "city not found"})

    weather = get_weather(city)
    assert weather is None
