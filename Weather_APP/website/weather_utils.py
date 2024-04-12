import calendar
import datetime
from datetime import datetime, date
import os
import requests
from flask import flash
from dotenv import load_dotenv
import matplotlib
matplotlib.use('Agg')
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

def fetch_air_quality_data(city):
    lat, lon = fetch_coordinates(city)
    if lat is None or lon is None:
        return None

    load_dotenv()
    api_key = os.getenv('API_KEY')
    air_quality_url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={api_key}"

    try:
        response = requests.get(air_quality_url).json()
        if 'list' in response:
            data = response['list'][0]
            air_quality_data = {
                'aqi': data['main']['aqi'],
                'co': data['components']['co'],
                'no': data['components']['no'],
                'no2': data['components']['no2'],
                'o3': data['components']['o3'],
                'so2': data['components']['so2'],
                'pm2_5': data['components']['pm2_5'],
                'pm10': data['components']['pm10'],
                'nh3': data['components']['nh3'],
                'timestamp': datetime.utcfromtimestamp(data['dt']).strftime('%Y-%m-%d %H:%M:%S')  # Includes timestamp of the data
            }
            return air_quality_data
        else:
            flash("Error fetching air quality data.", category='error')
            return None
    except requests.RequestException as e:
        flash(f"Failed to connect to air quality service: {e}", category='error')
        return None

def fetch_forecast_air_quality_data(city):
    lat, lon = fetch_coordinates(city)
    if lat is None or lon is None:
        return None

    load_dotenv()
    api_key = os.getenv('API_KEY')
    forecast_air_quality_url = f"http://api.openweathermap.org/data/2.5/air_pollution/forecast?lat={lat}&lon={lon}&appid={api_key}"

    try:
        response = requests.get(forecast_air_quality_url).json()
        if 'list' in response:
            return response['list']
        else:
            flash("Error fetching forecast air quality data.", category='error')
            return None
    except requests.RequestException as e:
        flash(f"Failed to connect to forecast air quality service: {e}", category='error')
        return None

def process_forecast_air_quality_data(forecast_data):
    processed_data = []
    for entry in forecast_data:
        processed_entry = {
            'dt': datetime.utcfromtimestamp(entry['dt']).strftime('%Y-%m-%d %H:%M:%S'),
            'aqi': entry['main']['aqi'],
            'co': entry['components']['co'],
            'no': entry['components']['no'],
            'no2': entry['components']['no2'],
            'o3': entry['components']['o3'],
            'so2': entry['components']['so2'],
            'pm2_5': entry['components']['pm2_5'],
            'pm10': entry['components']['pm10'],
            'nh3': entry['components']['nh3'],
        }
        processed_data.append(processed_entry)
    return processed_data


def fetch_historical_air_quality_data(city, start_timestamp, end_timestamp):
    lat, lon = fetch_coordinates(city)
    if lat is None or lon is None:
        return None

    load_dotenv()
    api_key = os.getenv('API_KEY')
    historical_air_quality_url = f"http://api.openweathermap.org/data/2.5/air_pollution/history?lat={lat}&lon={lon}&start={start_timestamp}&end={end_timestamp}&appid={api_key}"

    try:
        response = requests.get(historical_air_quality_url).json()
        if 'list' in response:
            return response['list']
        else:
            flash("Error fetching historical air quality data.", category='error')
            return None
    except requests.RequestException as e:
        flash(f"Failed to connect to historical air quality service: {e}", category='error')
        return None

def process_historical_air_quality_data(historical_data):
    processed_data = []
    for entry in historical_data:
        processed_entry = {
            'dt': datetime.utcfromtimestamp(entry['dt']).strftime('%Y-%m-%d %H:%M:%S'),
            'aqi': entry['main']['aqi'],
            'co': entry['components']['co'],
            'no': entry['components']['no'],
            'no2': entry['components']['no2'],
            'o3': entry['components']['o3'],
            'so2': entry['components']['so2'],
            'pm2_5': entry['components']['pm2_5'],
            'pm10': entry['components']['pm10'],
            'nh3': entry['components']['nh3'],
        }
        processed_data.append(processed_entry)
    return processed_data

# Constants for design
FIG_SIZE = (8, 5)
FONT_SIZE = 12
TITLE_SIZE = 14
LINE_WIDTH = 2
MARKER_SIZE = 8
GRID_COLOR = '#aaaaaa'

# Enhanced chart functions
def create_chart_base(title, x_label, y_label, figsize=FIG_SIZE):
    plt.figure(figsize=figsize)
    plt.title(title, fontsize=TITLE_SIZE, pad=20)
    plt.xlabel(x_label, fontsize=FONT_SIZE)
    plt.ylabel(y_label, fontsize=FONT_SIZE)
    plt.xticks(fontsize=FONT_SIZE)
    plt.yticks(fontsize=FONT_SIZE)
    plt.grid(color=GRID_COLOR, linestyle='--', linewidth=0.5)
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])

def save_chart(chart_path):
    # Ensure the directory for the chart exists
    directory = os.path.dirname(chart_path)
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    # Now save the chart as before
    plt.savefig(chart_path, bbox_inches='tight')
    plt.close()

def create_temperature_chart(processed_forecasts, chart_path='website/static/charts/temperature_chart.png'):
    days = [forecast['date'] for forecast in processed_forecasts]
    max_temps = [forecast['max_temp'] for forecast in processed_forecasts]
    min_temps = [forecast['min_temp'] for forecast in processed_forecasts]

    create_chart_base('5-Day Weather Forecast: Temperature', 'Day', 'Temperature (Celsius)')
    plt.plot(days, max_temps, label='Max Temperature', marker='o', color='red', linewidth=LINE_WIDTH, markersize=MARKER_SIZE)
    plt.plot(days, min_temps, label='Min Temperature', marker='o', color='blue', linewidth=LINE_WIDTH, markersize=MARKER_SIZE)
    plt.legend(fontsize=FONT_SIZE)
    save_chart(chart_path)

def create_humidity_chart(processed_forecasts, chart_path='website/static/charts/humidity_chart.png'):
    days = [forecast['date'] for forecast in processed_forecasts]
    humidity_levels = [forecast['humidity'] for forecast in processed_forecasts]

    create_chart_base('5-Day Weather Forecast: Humidity', 'Day', 'Humidity (%)')
    plt.bar(days, humidity_levels, color='cyan')
    save_chart(chart_path)

def create_wind_speed_chart(processed_forecasts, chart_path='website/static/charts/wind_speed_chart.png'):
    days = [forecast['date'] for forecast in processed_forecasts]
    wind_speeds = [forecast['wind_speed'] for forecast in processed_forecasts]

    create_chart_base('5-Day Weather Forecast: Wind Speed', 'Day', 'Wind Speed (km/h)')
    plt.plot(days, wind_speeds, label='Wind Speed', marker='>', linestyle='-', color='purple', linewidth=LINE_WIDTH, markersize=MARKER_SIZE)
    plt.legend(fontsize=FONT_SIZE)
    save_chart(chart_path)

def create_pressure_chart(processed_forecasts, chart_path='website/static/charts/pressure_chart.png'):
    days = [forecast['date'] for forecast in processed_forecasts]
    pressures = [forecast['pressure'] for forecast in processed_forecasts]

    create_chart_base('5-Day Weather Forecast: Atmospheric Pressure', 'Day', 'Pressure (hPa)')
    plt.plot(days, pressures, label='Atmospheric Pressure', marker='s', linestyle='--', color='green', linewidth=LINE_WIDTH, markersize=MARKER_SIZE)
    plt.legend(fontsize=FONT_SIZE)
    save_chart(chart_path)

def create_comparison_chart(processed_forecasts, chart_path='website/static/charts/comparison_chart.png'):
    days = [forecast['date'] for forecast in processed_forecasts]
    max_temps = [forecast['max_temp'] for forecast in processed_forecasts]
    humidities = [forecast['humidity'] for forecast in processed_forecasts]
    wind_speeds = [forecast['wind_speed'] for forecast in processed_forecasts]

    create_chart_base('5-Day Weather Forecast Comparison', 'Day', 'Value', figsize=(9, 5))

    # First y-axis for max temperature
    ax1 = plt.gca()
    ax1.set_ylabel('Max Temperature (Celsius)', color='tab:red', fontsize=FONT_SIZE)
    ax1.plot(days, max_temps, color='tab:red', label='Max Temp', marker='o', linewidth=LINE_WIDTH, markersize=MARKER_SIZE)
    ax1.tick_params(axis='y', labelcolor='tab:red')

    # Second y-axis for humidity
    ax2 = ax1.twinx()
    ax2.set_ylabel('Humidity (%)', color='tab:blue', fontsize=FONT_SIZE)
    ax2.plot(days, humidities, color='tab:blue', label='Humidity', marker='x', linewidth=LINE_WIDTH, markersize=MARKER_SIZE)
    ax2.tick_params(axis='y', labelcolor='tab:blue')

    # Third y-axis for wind speed
    ax3 = ax1.twinx()
    ax3.spines['right'].set_position(('outward', 60))
    ax3.set_ylabel('Wind Speed (km/h)', color='tab:green', fontsize=FONT_SIZE)
    ax3.plot(days, wind_speeds, color='tab:green', label='Wind Speed', marker='>', linewidth=LINE_WIDTH, markersize=MARKER_SIZE)
    ax3.tick_params(axis='y', labelcolor='tab:green')

    # Add all legends together
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    lines3, labels3 = ax3.get_legend_handles_labels()
    ax1.legend(lines + lines2 + lines3, labels + labels2 + labels3, loc='best', fontsize=FONT_SIZE)

    save_chart(chart_path)


