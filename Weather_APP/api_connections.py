import requests
from datetime import datetime
from dataclasses import dataclass
from collections import defaultdict
import statistics

# Uncomment the following lines if you want to use environment variables for your API key
# from dotenv import load_dotenv
# import os
#load_dotenv()
#api_key = os.getenv('API_KEY')

api_key = '87940aef71b9031ac2d5c12deb0c1be3'

@dataclass
class WeatherData:
    main: str
    description: str
    icon: str
    temperature: float

def degrees_to_compass(degrees):
    directions = ["North", "North-East", "East", "South-East", "South", "South-West", "West", "North-West"]
    index = int((degrees + 22.5) // 45) % 8
    return directions[index]

def get_lat_lon(city_name, api_key):
    base_url = "http://api.openweathermap.org/geo/1.0/direct"
    complete_url = f"{base_url}?q={city_name}&limit=1&appid={api_key}"
    try:
        response = requests.get(complete_url)
        response.raise_for_status()
        data = response.json()
        if data:
            lat = data[0]['lat']
            lon = data[0]['lon']
            return lat, lon
        else:
            return None, None
    except requests.RequestException as e:
        print(f"Error fetching coordinates: {e}")
        return None, None

def get_current_weather(lat, lon, api_key):
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    complete_url = f"{base_url}?lat={lat}&lon={lon}&appid={api_key}&units=metric"
    try:
        response = requests.get(complete_url)
        response.raise_for_status()
        resp = response.json()
        data = WeatherData(
            main=resp['weather'][0]['main'],
            description=resp['weather'][0]['description'],
            icon=resp['weather'][0]['icon'],
            temperature=resp['main']['temp']
        )
        return data
    except requests.RequestException as e:
        print(f"Error fetching weather data: {e}")
        return None

if __name__ == "__main__":
    city_name = input("Enter city name: ")
    lat, lon = get_lat_lon(city_name, api_key)
    if lat and lon:
        weather_data = get_current_weather(lat, lon, api_key)
        if weather_data:
            print(f"Weather in {city_name}: {weather_data.main}, {weather_data.description} with a temperature of {weather_data.temperature}°C.")
        else:
            print("Weather data not found.")
    else:
        print("City coordinates not found.")


# Display weather data in a structured format
#def display_weather_dashboard(weather_data):
    if weather_data:
        print(f"Weather Dashboard for {weather_data.get('name')} ({weather_data['coord']['lat']}, {weather_data['coord']['lon']})\n")
        print(f"Current Conditions: {weather_data['weather'][0]['main']} - {weather_data['weather'][0]['description']}")
        print(f"Temperature: {weather_data['main']['temp']}°C (Min: {weather_data['main']['temp_min']}°C, Max: {weather_data['main']['temp_max']}°C)")
        print(f"Humidity: {weather_data['main']['humidity']}%")
        print(f"Pressure: {weather_data['main']['pressure']} hPa")
        print(f"Visibility: {weather_data['visibility']/1000} km")
        print(f"Wind: {weather_data['wind']['speed']} m/s, Direction: {weather_data['wind']['deg']}°")
        print(f"Cloudiness: {weather_data['clouds']['all']}%")
        rain = weather_data.get('rain', {}).get('1h', 'No rain data')
        snow = weather_data.get('snow', {}).get('1h', 'No snow data')
        print(f"Rain: {rain}")
        print(f"Snow: {snow}")
        timestamp = datetime.fromtimestamp(weather_data['dt'], timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        print(f"Time of Data Calculation (UTC): {timestamp}")
    else:
        print("Failed to retrieve weather data.")


# Fetch 5 day 3 hour forecast data 
def get_forecast_data(lat, lon, api_key):
    base_url = "http://api.openweathermap.org/data/2.5/forecast"
    complete_url = f"{base_url}?lat={lat}&lon={lon}&appid={api_key}&units=metric"
    response = requests.get(complete_url).json()
    

# Display 5 day forecast data
def display_detailed_forecast_dashboard(forecast_data):
    if forecast_data:
        print("\nDetailed 5-Day Forecast:\n")
        
        # Organize forecast data by day
        daily_forecasts = defaultdict(list)
        for item in forecast_data['list']:
            date = datetime.fromtimestamp(item['dt']).strftime('%Y-%m-%d')
            daily_forecasts[date].append(item)
        
        # Display detailed forecast for each day
        for date, items in daily_forecasts.items():
            temps = [item['main']['temp'] for item in items]
            humidities = [item['main']['humidity'] for item in items]
            wind_speeds = [item['wind']['speed'] for item in items]
            descriptions = [item['weather'][0]['description'] for item in items]
            clouds = [item['clouds']['all'] for item in items]
            visibilities = [item.get('visibility', 10000) / 1000 for item in items]  # Default visibility set to 10 km
            
            avg_temp = statistics.mean(temps)
            max_temp = max(temps)
            min_temp = min(temps)
            avg_humidity = statistics.mean(humidities)
            avg_wind_speed = statistics.mean(wind_speeds)
            most_common_description = max(set(descriptions), key=descriptions.count)
            avg_clouds = statistics.mean(clouds)
            avg_visibility = statistics.mean(visibilities)
            
            # Convert average wind direction to compass bearing
            wind_direction_degrees = items[0]['wind']['deg']  # Example: Taking the first item's wind direction
            wind_direction_compass = degrees_to_compass(wind_direction_degrees)
            
            print(f"{date}:")
            print(f"  Avg Temp: {avg_temp:.2f}°C, Max Temp: {max_temp:.2f}°C, Min Temp: {min_temp:.2f}°C")
            print(f"  Humidity: {avg_humidity:.2f}%")
            print(f"  Conditions: {most_common_description}, Cloudiness: {avg_clouds:.2f}%")
            print(f"  Wind: Avg Speed: {avg_wind_speed:.2f} m/s, Direction: {wind_direction_compass}")
            print(f"  Visibility: {avg_visibility:.2f} km\n")
        
        else:
            print("Failed to retrieve forecast data.")
