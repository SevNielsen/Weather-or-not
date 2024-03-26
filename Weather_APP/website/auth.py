from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import Member
from werkzeug.security import generate_password_hash, check_password_hash
from . import db 
from flask_login import login_user, login_required, logout_user, current_user
#from datetime import datetime, timezone
from dotenv import load_dotenv
import os
import requests
import datetime
import calendar
import collections

auth = Blueprint('auth', __name__)

@auth.route('/login', methods = ['GET','POST'])
def login():
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
            flash("Incorrect username", category='error')
            #return redirect(url_for('auth.login'))

    return render_template("login.html", logged_in = current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/signup', methods = ['GET','POST'])
def sign_up():
    if request.method == 'POST':
        firstName = request.form.get('First_Name')
        lastName = request.form.get('Last_Name')
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        #city = request.form.get('city')

        member = Member.query.filter_by(username = username).first()
        if member:
            flash("member already exists", category='error')
            #return redirect(url_for('auth.sign_up'))

    
        elif firstName is None or lastName is None or email is None or password is None or username is None:
            flash("Please revise your information and try again", category="error")
        elif len(firstName) < 2 or len(lastName) < 2 or len(email) < 10 or len(password) < 2 or len(username) < 2:
            flash("Please provide enough characters and try again", category="error")
        #elif city is None or len(city) < 2:
            flash("Please Enter a Preferred City", category="error")
        else:
            #member = Member(username = username, first_name = firstName, last_name = lastName, email = email, city = city, password=generate_password_hash(password, method='pbkdf2:sha256'))
            member = Member(username = username, first_name = firstName, last_name = lastName, email = email, password=generate_password_hash(password, method='pbkdf2:sha256'))
            db.session.add(member)
            db.session.commit()
            login_user(member, remember=True)
            flash("Account created successfully", category="success")
            #return redirect(url_for('auth.profile'), logged_in =current_user)
            return redirect(url_for('auth.dashboard'))


    return render_template("signup.html", logged_in = current_user)

@auth.route('/dashboard', methods = ['GET','POST'])
@login_required
def dashboard():
    def weekday_from_date(day, month, year):
        return calendar.day_name[datetime.date(day=day, month=month, year=year).weekday()]
    
    load_dotenv()
    apikey = os.getenv('API_KEY')
    if request.method == 'POST':
        if request.form.get('city'):
            ci = request.form.get('city')
            url = 'https://api.openweathermap.org/data/2.5/weather?q={}&appid={}&units=metric'.format(ci, apikey)
            req = requests.get(url).json()
            lon, lat = req['coord'].get('lon'), req['coord'].get('lat')
            
    else:
        response = requests.get('https://api64.ipify.org?format=json').json()
        url = "http://ip-api.com/json/{}".format(response['ip'])
        response1 = requests.get(url).json()
        
        lon,lat,ci = response1['lon'], response1['lat'], response1['city']
        #current_user.city = ci
    
    current_user.city = ci

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
    #for date in listof:
        #year, month, day = date[3].split("-")
        #date[3] = weekday_from_date(int(day), int(month), int(year))
        #date[4] = 'https://openweathermap.org/img/wn/{}@2x.png'.format(date[4])

    return render_template("dashboard.html", logged_in=current_user, username=current_user.username, listof = listof1, cit2 = ci)

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

@auth.route('/bs', methods = ['GET','POST'])
@login_required
def bs():
    def weekday_from_date(day, month, year):
        return calendar.day_name[datetime.date(day=day, month=month, year=year).weekday()]
    if request.method == 'POST':
        # Extract city from form data
        city = request.form.get('city')
    else:
        # Use the user's default city or a predefined default
        city = current_user.city 
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
            "bs.html",
            logged_in=current_user.is_authenticated,
            current_weather=current_weather,
            forecast=sorted_forecast
        )
    except requests.RequestException:
        flash("Failed to connect to weather service", category='error') 
    return render_template("bs.html", logged_in=current_user.is_authenticated)

