import calendar
import datetime
from datetime import datetime
from datetime import date
import os
import requests
from flask import flash
from dotenv import load_dotenv
import matplotlib.pyplot as plt

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
        if len(processed_forecasts) >= 5:
            break 
        forecast_date = forecast.get('dt_txt').split()[0]
        if forecast_date != last_date:
            year, month, day = map(int, forecast_date.split("-"))
            weekday_name = weekday_from_date(year, month, day)

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

def weekday_from_date(year, month, day):
    try:
        valid_date = date(year, month, day)
        return calendar.day_name[valid_date.weekday()]
    except ValueError as e:
        print(f"Invalid date encountered: {e}")
        return "Invalid Date" 

def create_temperature_chart(processed_forecasts, chart_path='Weather_APP/website/static/charts/temprature_chart.png'):
    """Generate a temperature chart for the processed forecast data."""
    days = [forecast['date'] for forecast in processed_forecasts]
    max_temps = [forecast['max_temp'] for forecast in processed_forecasts]
    min_temps = [forecast['min_temp'] for forecast in processed_forecasts]
    
    plt.figure(figsize=(10, 6))
    plt.plot(days, max_temps, label='Max Temperature', marker='o', color='red')
    plt.plot(days, min_temps, label='Min Temperature', marker='o', color='blue')
    plt.title('5-Day Weather Forecast: Temperature')
    plt.xlabel('Day')
    plt.ylabel('Temperature (Celsius)')
    plt.legend()
    plt.grid(True)
    plt.savefig(chart_path)
    plt.close()

def create_humidity_chart(processed_forecasts, chart_path='Weather_APP/website/static/charts/humidity_chart.png'):
    """Generate a humidity chart for the processed forecast data."""
    days = [forecast['date'] for forecast in processed_forecasts]
    humidity_levels = [forecast['humidity'] for forecast in processed_forecasts]
    
    plt.figure(figsize=(10, 6))
    plt.bar(days, humidity_levels, color='cyan')
    plt.title('5-Day Weather Forecast: Humidity')
    plt.xlabel('Day')
    plt.ylabel('Humidity (%)')
    plt.savefig(chart_path)
    plt.close()

def create_wind_speed_chart(processed_forecasts, chart_path='Weather_APP/website/static/charts/wind_speed_chart.png'):
    """Generate a wind speed chart for the processed forecast data."""
    days = [forecast['date'] for forecast in processed_forecasts]
    wind_speeds = [forecast['wind_speed'] for forecast in processed_forecasts]
    
    plt.figure(figsize=(10, 6))
    plt.plot(days, wind_speeds, label='Wind Speed', marker='>', linestyle='-', color='purple')
    plt.title('5-Day Weather Forecast: Wind Speed')
    plt.xlabel('Day')
    plt.ylabel('Wind Speed (km/h)')
    plt.legend()
    plt.grid(True)
    plt.savefig(chart_path)
    plt.close()

def create_pressure_chart(processed_forecasts, chart_path='Weather_APP/website/static/charts/pressure_chart.png'):
    """Generate a pressure chart for the processed forecast data."""
    days = [forecast['date'] for forecast in processed_forecasts]
    pressures = [forecast['pressure'] for forecast in processed_forecasts]
    
    plt.figure(figsize=(10, 6))
    plt.plot(days, pressures, label='Atmospheric Pressure', marker='s', linestyle='--', color='green')
    plt.title('5-Day Weather Forecast: Atmospheric Pressure')
    plt.xlabel('Day')
    plt.ylabel('Pressure (hPa)')
    plt.legend()
    plt.grid(True)
    plt.savefig(chart_path)
    plt.close()

def create_comparison_chart(processed_forecasts, chart_path='Weather_APP/website/static/charts/comparison_chart.png'):
    """Generate a comparison chart for temperature, humidity, and wind speed."""
    days = [forecast['date'] for forecast in processed_forecasts]
    max_temps = [forecast['max_temp'] for forecast in processed_forecasts]
    humidities = [forecast['humidity'] for forecast in processed_forecasts]
    wind_speeds = [forecast['wind_speed'] for forecast in processed_forecasts]
    
    fig, ax1 = plt.subplots(figsize=(10, 6))

    color = 'tab:red'
    ax1.set_xlabel('Day')
    ax1.set_ylabel('Max Temperature (Celsius)', color=color)
    ax1.plot(days, max_temps, color=color, label='Max Temp', marker='o')
    ax1.tick_params(axis='y', labelcolor=color)

    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
    color = 'tab:blue'
    ax2.set_ylabel('Humidity (%)', color=color)
    ax2.plot(days, humidities, color=color, label='Humidity', marker='x')
    ax2.tick_params(axis='y', labelcolor=color)

    ax3 = ax1.twinx()
    ax3.spines['right'].set_position(('outward', 60))
    color = 'tab:green'
    ax3.set_ylabel('Wind Speed (km/h)', color=color)
    ax3.plot(days, wind_speeds, color=color, label='Wind Speed', marker='>')
    ax3.tick_params(axis='y', labelcolor=color)

    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    plt.title('5-Day Weather Forecast Comparison: Temperature, Humidity, and Wind Speed')
    fig.legend(loc="upper right", bbox_to_anchor=(1,1), bbox_transform=ax1.transAxes)
    plt.savefig(chart_path)
    plt.close()
