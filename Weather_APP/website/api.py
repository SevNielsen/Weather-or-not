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




load_dotenv()
apikey = os.getenv('API_KEY2')
city = 'Vancouver'
url = 'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{}/[date1]/[date2]?key=YOUR_API_KEY'.format(city,)