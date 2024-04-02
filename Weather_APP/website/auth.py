from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
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
from .weather_utils import weekday_from_date, fetch_weather_data, fetch_map_data, fetch_coordinates
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

@auth.route('/dashboard', methods = ['GET','POST'])
@login_required
def dashboard():
    if request.method == 'POST':
        # Extract city from form data
        city = request.form.get('city')
    else:
        # Use the user's default city or a predefined default
        city = current_user.city
    # Fetch Weather data from weather_utils api connection method
    '''
    weather_response, forecast_response = fetch_weather_data(city)
    if not weather_response or not forecast_response:
        return render_template("dashboard.html", logged_in=current_user.is_authenticated)
    #Parse Data for current weather
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
    '''
    load_dotenv()
    
    apikey = os.getenv('API_KEY')
    url = 'https://api.openweathermap.org/data/2.5/weather?q={}&appid={}&units=metric'.format(city, apikey)
    #'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric'
    req = requests.get(url).json()
    lon, lat = req['coord'].get('lon'), req['coord'].get('lat')

    url2 = 'https://api.openweathermap.org/data/2.5/forecast?lat={}&lon={}&appid={}&units=metric'.format(lat, lon, apikey)

    req2 = requests.get(url2).json()
    listof1 = []
    ha = -1
    for i in req2['list']:
        if ha == -1:
            temp = i.get('dt_txt').split()[0]
            year, month, day = temp.split("-")
            temp = weekday_from_date(int(day), int(month), int(year))
            listof1.append([int(i.get('main').get('temp_max')), int(i.get('main').get('temp_min')), i.get('weather')[0].get('description'), temp, 'https://openweathermap.org/img/wn/{}@2x.png'.format(i.get('weather')[0].get('icon'))])
            ha = ha + 1
        else:
            temp = i.get('dt_txt').split()[0]
            year, month, day = temp.split("-")
            temp = weekday_from_date(int(day), int(month), int(year))
            if temp == listof1[ha][3]:
                listof1[ha][0] = max(int(i.get('main').get('temp_max')), listof1[ha][0])
                listof1[ha][1] = min(int(i.get('main').get('temp_min')), listof1[ha][1])
                if listof1[ha][0] < i.get('main').get('temp_max'):
                    listof1[ha][4] = 'https://openweathermap.org/img/wn/{}@2x.png'.format(i.get('weather')[0].get('icon'))
                    listof1[ha][2] = i.get('weather')[0].get('description')
            else:
                ha = ha + 1
                listof1.append([int(i.get('main').get('temp_max')), int(i.get('main').get('temp_min')), i.get('weather')[0].get('description'), temp, 'https://openweathermap.org/img/wn/{}@2x.png'.format(i.get('weather')[0].get('icon'))])    
   
   
    #layer = "temp_new"  
    #zoom = 10  
    #map_url = fetch_map_data(layer, city, zoom) 
    return render_template("dashboard.html",logged_in=current_user,listof = listof1,username = current_user.username,cit2 = city)
        #current_weather=current_weather,
        #forecast=sorted_forecast,

        #map_url=map_url
    

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


