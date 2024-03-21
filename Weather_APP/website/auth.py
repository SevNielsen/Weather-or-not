from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import Member
from werkzeug.security import generate_password_hash, check_password_hash
from . import db 
from flask_login import login_user, login_required, logout_user, current_user
from dotenv import load_dotenv
import os
import requests
from datetime import datetime
import calendar
import collections
# Initialize the Blueprint for authentication routes
auth = Blueprint('auth', __name__)

@auth.route('/login', methods = ['GET','POST'])
def login():
    # Handle POST request to process login form submission
    if request.method == 'POST':
        username = request.form.get('``         username')
        password = request.form.get('password2')  ## Sam Jeon mr.perfecto183@gmail.com sammy ipad
        
        # Query the database for a user with the provided username
        member = Member.query.filter_by(username=username).first()
        if member and check_password_hash(member.password, password):
            # Log the user in and redirect to the dashboard
            login_user(member, remember=True)
            return redirect(url_for('auth.dashboard'))
        else:
            # Flash error message if login details are incorrect
            flash("Incorrect username or password", category='error')
    
    # Render login page for GET requests or after unsuccessful login attempt
    return render_template("login.html", logged_in=current_user.is_authenticated)

@auth.route('/logout')
@login_required
def logout():
    # Log the current user out and redirect to login page
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/signup', methods = ['GET','POST'])
def sign_up():
    # Handle POST request to process signup form submission
    if request.method == 'POST':
        # Collect from data
        firstName = request.form.get('First_Name')
        lastName = request.form.get('Last_Name')
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
       # Check if a user with the provided username already exists
        member = Member.query.filter_by(username=username).first()
        if member:
            flash("Username already exists", category='error')
        elif not all([firstName, lastName, email, password, username]):
            flash("All fields are required", category='error')
        else:
            # Create new member and add to the database
            new_member = Member(
                username=username, 
                first_name=firstName, 
                last_name=lastName, 
                email=email, 
                password=generate_password_hash(password, method='pbkdf2:sha256')
            )
            db.session.add(new_member)
            db.session.commit()
            # Log the user in and redirect to the profile page
            login_user(new_member, remember=True)
            flash("Account created successfully", category="success")
            return redirect(url_for('auth.profile'))
    # Render signup page for GET requests or after unsuccessful signup attempt
    return render_template("signup.html", logged_in = current_user)

@auth.route('/dashboard', methods = ['GET','POST'])
@login_required
def dashboard():   
    # Default city
    default_city = 'Vancouver'
    if request.method == 'POST':
        # Extract city from form data
        city = request.form.get('city')
    else:
        # Use the user's default city or a predefined default
        city = current_user.city if current_user.city else default_city
    # Load API key from .env file
    load_dotenv()
    api_key = os.getenv('API_KEY')
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
        daily_forecasts = collections.defaultdict(lambda: {
            'temp_max': float('-inf'),
            'temp_min': float('inf'),
            'icons': [],
            'descriptions': [],
            'day': '',
            'date': ''
        })
        # Process and aggregate data
        for entry in forecast_response['list']:
            date_text = entry['dt_txt']
            date_obj = datetime.strptime(date_text, '%Y-%m-%d %H:%M:%S')
            date = date_text[:10]  # Extract just the date part
            weekday = calendar.day_name[date_obj.weekday()]
            
            # Aggregate data
            daily_forecasts[date]['temp_max'] = max(daily_forecasts[date]['temp_max'], entry['main']['temp_max'])
            daily_forecasts[date]['temp_min'] = min(daily_forecasts[date]['temp_min'], entry['main']['temp_min'])
            if entry['weather'][0]['icon'] not in daily_forecasts[date]['icons']:
                daily_forecasts[date]['icons'].append(entry['weather'][0]['icon'])
            if entry['weather'][0]['description'] not in daily_forecasts[date]['descriptions']:
                daily_forecasts[date]['descriptions'].append(entry['weather'][0]['description'])
            daily_forecasts[date]['day'] = weekday
            daily_forecasts[date]['date'] = date

        # Convert aggregated data into a sorted list by date
        sorted_forecast = [value for key, value in sorted(daily_forecasts.items(), key=lambda x: x[0])][:5]

        # Prepare the forecast data for each day
        for day_forecast in sorted_forecast:
            day_forecast['icon'] = day_forecast['icons'][0]  # Example: use the first icon, or choose based on logic
            day_forecast['description'] = ', '.join(set(day_forecast['descriptions']))  # Combine all descriptions
        return render_template(
            "dashboard.html",
            logged_in=current_user.is_authenticated,
            current_weather=current_weather,
            forecast=sorted_forecast
        )
    except requests.RequestException:
        flash("Failed to connect to weather service", category='error') 
    
    return render_template("dashboard.html", logged_in=current_user.is_authenticated)


@auth.route('/profile', methods = ['GET','POST'])
@login_required
def profile():
    if request.method == 'POST':
        if request.form.get('first_name'):
            current_user.first_name = request.form.get('first_name')
        if request.form.get('last_name'):
            current_user.last_name = request.form.get('last_name')
        if request.form.get('email'):
            current_user.email = request.form.get('email')
        #if request.form.get('username'):
        #   current_user.username = request.form.get('username')
        if request.form.get('city'):
            current_user.city = request.form.get('city')
        if request.form.get('check'):
            current_user.notifications = True
        else:
            current_user.notifications = False
        flash('Successfully Made Changes to Your Profile',category='changed')
        db.session.commit()
    return render_template("profile.html", logged_in = current_user, username = current_user.username, firstName = current_user.first_name, lastName = current_user.last_name, email = current_user.email, notifications = current_user.notifications, city = current_user.city )

@auth.route('/bs')
@login_required
def testing():
    return render_template("bs.html", logged_in=current_user.is_authenticated, username=current_user.username)
