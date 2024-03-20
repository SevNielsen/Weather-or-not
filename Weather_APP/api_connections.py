import requests
from datetime import datetime
from dataclasses import dataclass
from collections import defaultdict
import statistics
from flask import flash

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

'''
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
'''

'''
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

'''

def call_current_weather_API(lat, lon, apikey):
    # Fetching current weather data 
    current_weather_url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={apikey}&units=metric"
    try:
        current_weather_response = requests.get(current_weather_url).json()
        # Ensure the API request was successful
        if current_weather_response.get('cod') != 200:
            return None, 'Could not retrieve weather data. Please try again.'

        # Parse data into dictionary format
        current_weather_data = {
            'icon': f"https://openweathermap.org/img/wn/{current_weather_response['weather'][0]['icon']}@2x.png",
            'temperature': current_weather_response['main']['temp'],
            'feels_like': current_weather_response['main']['feels_like'],
            'temp_min': current_weather_response['main']['temp_min'],
            'temp_max': current_weather_response['main']['temp_max'],
            'humidity': current_weather_response['main']['humidity'],
            'city': current_weather_response['name'],
            'sunrise': datetime.datetime.fromtimestamp(current_weather_response['sys']['sunrise']).strftime('%Y-%m-%d %H:%M:%S'),
            'sunset': datetime.datetime.fromtimestamp(current_weather_response['sys']['sunset']).strftime('%Y-%m-%d %H:%M:%S'),
        }
        return current_weather_data, None
    except requests.RequestException as e:
        return None, f'An error occurred: {e}'
    
def dashboard():
    # Load API key from .env file
    #load_dotenv()
    api_key = 'a077f033d014870da9c49ee6f07c59b8'
    # Default city to use if the user has not set one
    city = 'Vancouver'

    # Fetching current weather data 
    weather_url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric'
    forecast_url = f'https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric'

        # Make requests to OpenWeatherMap API
    try:
        weather_response = requests.get(weather_url).json()
        forecast_response = requests.get(forecast_url).json()

        if weather_response.get('cod') != '200':
            flash(f"Error fetching current weather: {weather_response.get('message', 'Unknown error')}", category='error')
        
        if forecast_response.get('cod') != '200':
            flash(f"Error fetching forecast: {forecast_response.get('message', 'Unknown error')}", category='error')

        current_weather = {
            'icon': f"https://openweathermap.org/img/wn/{weather_response['weather'][0]['icon']}@2x.png",
            'temperature': weather_response['main']['temp'],
            'feels_like': weather_response['main']['feels_like'],
            'temp_min': weather_response['main']['temp_min'],
            'temp_max': weather_response['main']['temp_max'],
            'humidity': weather_response['main']['humidity'],
            'city': weather_response['name'],
            'sunrise': datetime.fromtimestamp(weather_response['sys']['sunrise']).strftime('%H:%M'),
            'sunset': datetime.fromtimestamp(weather_response['sys']['sunset']).strftime('%H:%M'),
        }
        forecast_data = []
        for entry in forecast_response['list']:
            date_text = entry['dt_txt']
            date_obj = datetime.strptime(date_text, '%Y-%m-%d %H:%M:%S')
            weekday = calendar.day_name[date_obj.weekday()]
            forecast_data.append({
                'day': weekday,
                'date': date_text[:10],
                'temp_max': entry['main']['temp_max'],
                'temp_min': entry['main']['temp_min'],
                'icon': f"https://openweathermap.org/img/wn/{entry['weather'][0]['icon']}@2x.png",
                'description': entry['weather'][0]['description']
            })
        # Group forecast data by day for display
        grouped_forecast = {}
        for entry in forecast_data:
            day = entry['date']
            if day not in grouped_forecast:
                grouped_forecast[day] = entry
            else:
                # Update max/min temperatures if necessary
                grouped_forecast[day]['temp_max'] = max(grouped_forecast[day]['temp_max'], entry['temp_max'])
                grouped_forecast[day]['temp_min'] = min(grouped_forecast[day]['temp_min'], entry['temp_min'])
        
        # Convert grouped forecast data to a list sorted by date
        sorted_forecast = [value for key, value in sorted(grouped_forecast.items())]
    
        return render_template(
            "dashboard.html",
            logged_in=current_user.is_authenticated,
            current_weather=current_weather,
            forecast=sorted_forecast
        )
    except requests.RequestException:
        flash("Failed to connect to weather service", category='error') 
    
    return render_template("dashboard.html", logged_in=current_user.is_authenticated)
    