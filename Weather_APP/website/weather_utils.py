import calendar
import datetime
import os
import requests
from flask import flash
from dotenv import load_dotenv

#Convert a given date to its corresponding weekday name.
def weekday_from_date(day, month, year):
    return calendar.day_name[datetime.date(day=day, month=month, year=year).weekday()]

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

#Fetch current weather and forecast data for a given city.
def fetch_weather_data(city):
    load_dotenv()
    api_key = os.getenv('API_KEY')
    weather_url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric'
    forecast_url = f'https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric'
    try:
        weather_response = requests.get(weather_url).json()
        forecast_response = requests.get(forecast_url).json()
        if weather_response.get('cod') != '200' or forecast_response.get('cod') != '200':
            flash("Error fetching weather data.", category='error')
            return None, None
        print(weather_response)
        return weather_response, forecast_response
    except requests.RequestException:
        flash("Failed to connect to weather service", category='error')
        return None, None

    

