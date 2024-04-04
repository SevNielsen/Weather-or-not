import calendar
import datetime
from datetime import datetime
from datetime import date
import os
import requests
from flask import flash
from dotenv import load_dotenv

def weekday_from_date(day, month, year):
    try:
        # Check if the year, month, and day combination is valid
        valid_date = date(year, month, day)
        return calendar.day_name[valid_date.weekday()]
    except ValueError as e:
        print(f"Invalid date encountered: {e}")
        
        return "2024"

def fetch_coordinates(city):
    load_dotenv()
    api_key = os.getenv('API_KEY')
    geocode_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={api_key}"
    try:
        response = requests.get(geocode_url).json()
        if response:
            # Assuming the first result is the most relevant one
            latitude = response[0]['lat']
            longitude = response[0]['lon']
            return latitude, longitude
        else:
            flash("City not found or API error occurred.", category='error')
            return None, None
    except requests.RequestException:
        flash("Failed to connect to geolocation service", category='error')
        return None, None

#Fetch map tile data.
def fetch_map_data(layer, zoom, lat, lon):
    load_dotenv()
    api_key = os.getenv('API_KEY')
    map_url = f"https://tile.openweathermap.org/map/{layer}/{zoom}/{lat}/{lon}.png?appid={api_key}"
    try:
        # Actual fetching of the image is done by the client's browser.
        return map_url
    except Exception as e:
        flash(f"Failed to build map data URL: {e}", category='error')
        return None

def fetch_current_weather_data(city):
    load_dotenv()
    api_key = os.getenv('API_KEY')
    weather_url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric'
    
    try:
        response = requests.get(weather_url).json()
        if response.get('cod') == 200:
            sunrise_time = datetime.utcfromtimestamp(response['sys']['sunrise']).strftime('%Y-%m-%d %H:%M:%S')
            sunset_time = datetime.utcfromtimestamp(response['sys']['sunset']).strftime('%Y-%m-%d %H:%M:%S')

            current_weather = {
                'temperature': response['main']['temp'],
                'feels_like': response['main']['feels_like'],
                'temperature_min': response['main']['temp_min'],
                'temperature_max': response['main']['temp_max'],
                'pressure': response['main']['pressure'],
                'humidity': response['main']['humidity'],
                'weather_description': response['weather'][0]['description'],
                'icon': f"https://openweathermap.org/img/wn/{response['weather'][0]['icon']}@2x.png",
                'wind_speed': response['wind']['speed'],
                'wind_deg': response['wind']['deg'],
                'clouds': response['clouds']['all'],
                'visibility': response.get('visibility', 'N/A'),  # Not all responses include visibility
                'sunrise': sunrise_time,
                'sunset': sunset_time,
                'city': response['name'],
                'country': response['sys']['country'],
            }
            return current_weather
        else:
            flash("Error fetching current weather data.", category='error')
    except requests.RequestException as e:
        flash(f"Failed to connect to weather service: {e}", category='error')
    
    return None

def fetch_forecast_data(lat, lon, api_key):
    forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={api_key}&units=metric"
    try:
        response = requests.get(forecast_url)
        response.raise_for_status()  # Raises stored HTTPError, if one occurred.
        return response.json()
    except requests.HTTPError as http_err:
        flash(f"HTTP error occurred: {http_err}", category='error')
    except Exception as err:
        flash(f"Other error occurred: {err}", category='error')
    return None

def process_forecast_data(forecast_json):
    processed_forecasts = []
    last_date = ""
    for forecast in forecast_json['list']:
        forecast_date = forecast.get('dt_txt').split()[0]
        if forecast_date != last_date:
            # Extract date components and compute the weekday name
            year, month, day = forecast_date.split("-")
            weekday_name = weekday_from_date(int(year), int(month), int(day))

            # Prepare additional data points from the forecast
            weather_data = forecast.get('weather')[0]
            main_data = forecast.get('main')
            wind_data = forecast.get('wind')

            processed_forecasts.append({
                'date': f"{weekday_name}, {day}/{month}",
                'max_temp': int(main_data.get('temp_max')),
                'min_temp': int(main_data.get('temp_min')),
                'description': weather_data.get('description'),
                'icon': f"https://openweathermap.org/img/wn/{weather_data.get('icon')}@2x.png",
                'humidity': main_data.get('humidity'),
                'pressure': main_data.get('pressure'),
                'wind_speed': wind_data.get('speed'),
                'wind_deg': wind_data.get('deg'),
                # Additional fields can be added here as needed
            })
            last_date = forecast_date
    return processed_forecasts
