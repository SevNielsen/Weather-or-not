from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from .models import Member
from werkzeug.security import generate_password_hash, check_password_hash
from . import db 
from flask_login import login_user, login_required, logout_user, current_user
from dotenv import load_dotenv
import os
from .weather_utils import (
    fetch_current_weather_data, fetch_coordinates,
    fetch_forecast_data, process_forecast_data,
    create_temperature_chart, create_humidity_chart,
    create_wind_speed_chart, create_pressure_chart,
    create_comparison_chart )
# Initialize the Blueprint for authentication routes
auth = Blueprint('auth', __name__)


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
    if request.method == 'POST':
        city = request.form.get('city')
    else:
        city = current_user.city
    current_weather = fetch_current_weather_data(city)
    forecasts = None
    lat, lon = fetch_coordinates(city)
    if lat is not None and lon is not None:
        forecast_json = fetch_forecast_data(lat, lon, os.getenv('API_KEY'))
        if forecast_json:
            forecasts = process_forecast_data(forecast_json)
            create_temperature_chart(forecasts, 'Weather_APP/website/static/charts/temperature_chart.png')
            create_humidity_chart(forecasts, 'Weather_APP/website/static/charts/humidity_chart.png')
            create_wind_speed_chart(forecasts, 'Weather_APP/website/static/charts/wind_speed_chart.png')
            create_pressure_chart(forecasts, 'Weather_APP/website/static/charts/pressure_chart.png')
            create_comparison_chart(forecasts, 'Weather_APP/website/static/charts/comparison_chart.png')
    return render_template("dashboard.html", logged_in=current_user.is_authenticated, current_weather=current_weather, forecasts=forecasts, username=current_user.username, city=city, lat=lat, lon=lon)
   



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
    return render_template("profile.html", logged_in = current_user, username = current_user.username, firstName = current_user.first_name, lastName = current_user.last_name, email = current_user.email, notifications = current_user.notifications, city = current_user.city )

@auth.route('/leafletMap')
@login_required
def showMap():
    return render_template('leafletMap.html', logged_in=current_user.is_authenticated)

@auth.route('/config')
def config():
    api_key = os.getenv('API_KEY')
    if api_key is None:
        # Return a json with error message if API key is not found
        return jsonify({"error": "API key is not set"}), 500
    return jsonify(apiKey=api_key)
