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
        member = Member.query.filter_by(username = username).first()
        if member:
            flash("member already exists", category='error')
            #return redirect(url_for('auth.sign_up'))

    
        elif firstName is None or lastName is None or email is None or password is None or username is None:
            flash("Please revise your information and try again", category="error")
        elif len(firstName) < 2 or len(lastName) < 2 or len(email) < 10 or len(password) < 2 or len(username) < 2:
            flash("Please provide enough characters and try again", category="error")
        else:
            member = Member(username = username, first_name = firstName, last_name = lastName, email = email, password=generate_password_hash(password, method='pbkdf2:sha256'))
            db.session.add(member)
            db.session.commit()
            login_user(member, remember=True)
            flash("Account created successfully", category="success")
            #return redirect(url_for('auth.profile'), logged_in =current_user)
            return redirect(url_for('auth.profile'))


    return render_template("signup.html", logged_in = current_user)

@auth.route('/dashboard', methods = ['GET','POST'])
def dashboard():
    '''
    def weekday_from_date(day, month, year):
    return calendar.day_name[
        datetime.date(day=day, month=month, year=year).weekday()
    ]
    load_dotenv()
    apikey = os.getenv('API_KEY')
    url = 'https://api.openweathermap.org/data/2.5/weather?q={}&appid={}&units=metric'.format(current_user.city, apikey)
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
            listof1.append([int(i.get('main').get('temp_max')), int(i.get('main').get('temp_min')), i.get('weather')[0].get('description'), temp, i.get('weather')[0].get('icon')])
            ha = ha + 1
        else:
            temp = i.get('dt_txt').split()[0]
            year, month, day = temp.split("-")
            temp = weekday_from_date(int(day), int(month), int(year))
            if i.get('dt_txt').split()[0] == listof1[ha][3]:
                listof1[ha][0] = max(int(i.get('main').get('temp_max')), listof1[ha][0])
                listof1[ha][1] = min(int(i.get('main').get('temp_min')), listof1[ha][1])
            else:
                ha = ha + 1
                listof1.append([int(i.get('main').get('temp_max')), int(i.get('main').get('temp_min')), i.get('weather')[0].get('description'), i.get('dt_txt').split()[0], i.get('weather')[0].get('icon')])
    #for date in listof:
        #year, month, day = date[3].split("-")
        #date[3] = weekday_from_date(int(day), int(month), int(year))
        #date[4] = 'https://openweathermap.org/img/wn/{}@2x.png'.format(date[4])
'''
    return render_template("dashboard.html", logged_in=current_user, username=current_user.username)#,listof = listof1)

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
        flash('Successfully Made Changes to Your Profile',category='changed')
        db.session.commit()
        


  #  username1 = current_user.username
   # firstName1 = current_user.first_name
   # lastName1 = current_user.last_name
   # email1 = current_user.email
   # notification1 = current_user.notifications
  #  city1 = current_user.city
    return render_template("profile.html", logged_in = current_user, username = current_user.username, firstName = current_user.first_name, lastName = current_user.last_name, email = current_user.email, notifications = current_user.notifications, city = current_user.city )
#   return render_template("profile.html")

@auth.route('/bs')
def testing():
    username1 = current_user.username
    return render_template("bs.html", logged_in = current_user, username = username1)
