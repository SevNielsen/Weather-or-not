import calendar
import datetime
import os
import requests
from flask import flash
from dotenv import load_dotenv

#Convert a given date to its corresponding weekday name.
def weekday_from_date(day, month, year):
    return calendar.day_name[datetime.date(day=day, month=month, year=year).weekday()]

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


def fetch_map_data(city):
    load_dotenv()
    api_key = os.getenv('API_KEY')
    