from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from .models import Member,Visit, Config,db
from werkzeug.security import generate_password_hash, check_password_hash
from . import db, auth
from sqlalchemy import func
from . import db, auth
from sqlalchemy import func
from flask_login import login_user, login_required, logout_user, current_user
from dotenv import load_dotenv
import os
import requests
from datetime import datetime
from twilio.rest import Client
import calendar
import collections
from .weather_utils import (
    fetch_current_weather_data, fetch_coordinates,
    fetch_forecast_data, process_forecast_data,
    create_temperature_chart, create_humidity_chart,
    create_wind_speed_chart, create_pressure_chart,
    create_comparison_chart )


# Initialize the Blueprint for authentication routes
auth = Blueprint('auth', __name__)


# Twilio Configuration
account_sid = 'YOUR_TWILIO_ACCOUNT_SID'
auth_token = 'YOUR_TWILIO_AUTH_TOKEN'
twilio_phone_number = 'YOUR_TWILIO_PHONE_NUMBER'

client = Client(account_sid, auth_token)


@auth.before_app_request
def record_visit():
    # Filter out requests for static resources
    if request.endpoint and "static" in request.endpoint:
        return
    today = datetime.utcnow().date()
    visit = Visit.query.filter_by(date=today).first()
    if visit:
        visit.count += 1
    else:
        visit = Visit(date=today, count=1)
        db.session.add(visit)
    db.session.commit()

@auth.route('/')
def home():
    return render_template("welcome.html")


@auth.route('/login', methods = ['GET','POST']) #change from login2 --> login
def login():
    # Handle POST request to process login form submission
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password2')  ## Sam Jeon mr.perfecto183@gmail.com sammy ipad
        member = Member.query.filter_by(username = username).first()
        if member:
            if check_password_hash(member.password, password):
                login_user(member, remember=True)
                #flash("Successfully Lo", category='success')
                return redirect(url_for('auth.dashboard'))
                #return redirect(url_for('auth.dashboard'))
            else:
                flash("Incorrect Password", category='error')
                #return redirect(url_for('auth.login'))

        else:
            # Flash error message if login details are incorrect
            flash("Incorrect username or password", category='error')
    
    return render_template("login.html", logged_in=current_user) 

@auth.route('/logout')
@login_required
def logout():
    # Log the current user out and redirect to login page
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/signup', methods = ['GET','POST'])
def sign_up():
    #Check if user registration is allowed
    config = Config.query.filter_by(key='allow_registration').first()
    if not config or config.value != 'true':
        flash('Registration is currently disabled.', 'error')
        return redirect(url_for('auth.login'))
    
    # Handle POST request to process signup form submission
    if request.method == 'POST':
        # Collect from data
        firstName = request.form.get('First_Name')
        lastName = request.form.get('Last_Name')
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        city = request.form.get('city')

        member = Member.query.filter_by(username = username).first()
        if member:
            flash("member already exists", category='error')
            #return redirect(url_for('auth.sign_up'))

    
        elif firstName is None or lastName is None or email is None or password is None or username is None:
            flash("Please revise your information and try again", category="error")
        elif len(firstName) < 2 or len(lastName) < 2 or len(email) < 10 or len(password) < 2 or len(username) < 2:
            flash("Please provide enough characters and try again", category="error")
        elif city is None or len(city) < 2:
            flash("Please Enter a Preferred City", category="error")
        else:
            member = Member(username = username, first_name = firstName, last_name = lastName, email = email, city = city, password=generate_password_hash(password, method='pbkdf2:sha256'))
            db.session.add(member)
            db.session.commit()
            login_user(member, remember=True)
            #login_user(new_member, remember=True)
            flash("Account created successfully", category="success")
            #return redirect(url_for('auth.profile'), logged_in =current_user)
            return redirect(url_for('auth.dashboard'))


    return render_template("signup.html", logged_in = current_user)

@auth.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    current_weather = None
    forecasts = None
    city = current_user.city if current_user.city else 'Default City'
    chart_paths = {
        'temperature_chart': None,
        'humidity_chart': None,
        'wind_speed_chart': None,
        'pressure_chart': None,
        'comparison_chart': None
    }

    if request.method == 'POST':
        city = request.form.get('city', '').strip()
        if not city:
            flash('Please enter a city name.', 'error')
            city = current_user.city if current_user.city else 'Default City'
            return redirect(url_for('auth.dashboard'))

        lat, lon = fetch_coordinates(city)
        if lat is None or lon is None:
            flash('Invalid city name. Please try another.', 'error')
            return redirect(url_for('auth.dashboard'))

        current_weather = fetch_current_weather_data(city)
        if current_weather is None:
            flash('Unable to fetch weather for the specified city.', 'error')
            return redirect(url_for('auth.dashboard'))

        forecast_json = fetch_forecast_data(lat, lon, os.getenv('API_KEY'))
        if forecast_json:
            forecasts = process_forecast_data(forecast_json)
            chart_paths['temperature_chart'] = create_temperature_chart(forecasts, 'website/static/charts/temperature_chart.png')
            chart_paths['humidity_chart'] = create_humidity_chart(forecasts, 'website/static/charts/humidity_chart.png')
            chart_paths['wind_speed_chart'] = create_wind_speed_chart(forecasts, 'website/static/charts/wind_speed_chart.png')
            chart_paths['pressure_chart'] = create_pressure_chart(forecasts, 'website/static/charts/pressure_chart.png')
            chart_paths['comparison_chart'] = create_comparison_chart(forecasts, 'website/static/charts/comparison_chart.png')
    else:
        # Use preferred city on initial GET request
        lat, lon = fetch_coordinates(city)
        if lat and lon:
            current_weather = fetch_current_weather_data(city)
            forecast_json = fetch_forecast_data(lat, lon, os.getenv('API_KEY'))
            if forecast_json:
                forecasts = process_forecast_data(forecast_json)
                # Update chart paths as above

    return render_template("dashboard.html", logged_in=current_user.is_authenticated, 
                           current_weather=current_weather, forecasts=forecasts, 
                           chart_paths=chart_paths, username=current_user.username, city=city, lat=lat, lon=lon)


   
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

        #if request.form.get('check'):
        #    current_user.notifications = request.form.get(bool(int(request.form.get('check'))))
        if request.form.get('check'):
            current_user.notifications = True
        else:
            current_user.notifications = False
        db.session.commit()
        flash('Successfully Made Changes to Your Profile',category='success')
    return render_template("profile.html", logged_in = current_user.is_authenticated, username = current_user.username, firstName = current_user.first_name, lastName = current_user.last_name, email = current_user.email, notifications = current_user.notifications, city = current_user.city )

@auth.route('/leafletMap')
@login_required
def showMap():
    default_lat, default_lon = 49.886, -119.496  #Kelowna
    city = current_user.city if current_user.city else None
    if city:
        lat, lon = fetch_coordinates(city)
        if lat is None or lon is None: 
            lat, lon = default_lat, default_lon
    else:
        lat, lon = default_lat, default_lon

    return render_template('leafletMap.html', logged_in=current_user.is_authenticated, lat=lat, lon=lon)


@auth.route('/config')
def config():
    api_key = os.getenv('API_KEY')
    if api_key is None:
        # Return a json with error message if API key is not found
        return jsonify({"error": "API key is not set"}), 500
    return jsonify(apiKey=api_key)
     

@auth.route('/update_role/<int:user_id>', methods=['POST'])
@login_required
def update_role(user_id):
    if not current_user.is_admin:
        flash('Only admins can perform this action.', 'error')
        return redirect(url_for('auth.login'))

    if current_user.id == user_id:
        # Check if attempting to change the role of the current admin user

        flash("Administrators cannot change their own admin status.", 'error')
        return redirect(url_for('auth.admin_dashboard'))

    user = Member.query.get(user_id)
    if user:
        new_role_is_admin = request.form.get('is_admin') == 'on'
        if user.is_admin and not new_role_is_admin and user_id == current_user.id:
         # Prevent administrators from setting themselves as non-administrators
            flash("Administrators cannot remove their own administrator privileges.", 'error')
        else:
            user.is_admin = new_role_is_admin
            db.session.commit()
            flash('User role updated successfully.', 'success')
    else:
        flash('User not found.', 'error')

    return redirect(url_for('auth.admin_dashboard'))

@auth.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        flash('Only admins can perform this action.', 'error')
        return redirect(url_for('auth.login'))

    user = Member.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully.', 'success')
    else:
        flash('User not found.', 'error')

    return redirect(url_for('auth.admin_dashboard'))

@auth.route('/admin/dashboard', methods=['GET', 'POST'])
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('Access restricted to administrators only.', 'error')
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        # Handle website configuration update
        allow_registration = 'true' if request.form.get('allow_registration') else 'false'
        config = Config.query.filter_by(key='allow_registration').first()
        if config:
            config.value = allow_registration
        else:
            db.session.add(Config(key='allow_registration', value=allow_registration))
        db.session.commit()
        flash('Configuration updated successfully.', 'success')
        return redirect(url_for('auth.admin_dashboard'))

    users = Member.query.all()
    config = Config.query.filter_by(key='allow_registration').first()
    allow_registration = config.value if config else 'false'
    total_users = Member.query.count()
    total_visits = Visit.query.count()  # Obtaining total visits
    cities = db.session.query(Member.city).filter(Member.city != None).distinct().all()
    cities = [city[0] for city in cities]  

    no_cities_available = False 
    if not cities:
        no_cities_available = True 
    return render_template('admin_dashboard.html', 
                           users=users, 
                           allow_registration=allow_registration == 'true', 
                           total_visits=total_visits, 
                           total_users=total_users,
                           cities=cities, 
                           no_cities_available=no_cities_available)

@auth.route('/admin/login', methods=['GET', 'POST'])  # change from login2 --> login
def admin_login():
    # Handle POST request to process login form submission
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password2')  ## Sam Jeon mr.perfecto183@gmail.com sammy ipad
        member = Member.query.filter_by(username=username, is_admin=1).first()
        if member:
            if check_password_hash(member.password, password):
                login_user(member, remember=True)
                # flash("Successfully Lo", category='success')
                return redirect(url_for('auth.admin_dashboard'))
                # return redirect(url_for('auth.dashboard'))
            else:
                flash("Incorrect Password", category='error')
                # return redirect(url_for('auth.login'))

        else:
            # Flash error message if login details are incorrect
            flash("Incorrect username or password", category='error')

    return render_template("admin_login.html", logged_in=current_user)

@auth.route('/update_notifications/<int:user_id>', methods=['POST'])
def update_notifications(user_id):
    user = Member.query.get(user_id)
    if user:
        # Update user notification settings
        user.notifications = bool(request.form.get('notifications', False))
        db.session.commit()

        # If user opts to receive notifications, send a text message
        if user.notifications:
            send_sms(user.phone_number, "Your application notifications have been updated.")

    return redirect(url_for('auth.admin_dashboard'))

def send_sms(phone_number, message):
    try:
        
        message = client.messages.create(
            to=phone_number,
            from_=twilio_phone_number,
            body=message
        )
        print(f"SMS notification sent to {phone_number}")
        return True
    except Exception as e:
        print(f"Error sending SMS notification: {e}")
        return False


@auth.route('/notify_all', methods=['POST'])
@login_required
def notify_all():
    users = Member.query.all()
    successful_count = 0

    for user in users:
        if send_sms(user.phone_number, "This is a notification for all users."):
            successful_count += 1

    if successful_count == len(users):
        flash('All users have been notified.', 'success')
    else:
        flash(f'Notified {successful_count} out of {len(users)} users.', 'warning')
    
    return redirect(url_for('auth.admin_dashboard'))


@auth.route('/notify_by_city', methods=['POST'])
@login_required
def notify_by_city():
    city = request.form['city']
    message = request.form['message']
    users = Member.query.filter_by(city=city).all()

    if not users:
        flash('No users found in the specified city.', 'error')
        return redirect(url_for('auth.admin_dashboard'))

    successful_count = 0
    for user in users:
        if send_sms(user.phone_number, message):
            successful_count += 1

    if successful_count == len(users):
        flash(f'Notification sent to all users in {city}.', 'success')
    else:
        flash(f'Notified {successful_count} out of {len(users)} users in {city}.', 'warning')
    
    return redirect(url_for('auth.admin_dashboard'))


@auth.route('/notify_individual', methods=['POST'])
@login_required
def notify_individual():
    user_id = request.form.get('user_id')
    message = request.form.get('message')
    user = Member.query.get(user_id)
    if user:
        if send_sms(user.phone_number, message):
            flash(f'Notification sent successfully to {user.username}.', 'success')
        else:
            flash('Failed to send notification.', 'error')
    else:
        flash('User not found.', 'error')
    return redirect(url_for('auth.admin_dashboard'))
