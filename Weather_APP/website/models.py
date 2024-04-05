from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class WeatherPreference(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'))
    temp_threshold = db.Column(db.Float)
    temp_condition = db.Column(db.String(50))
    wind_speed_threshold = db.Column(db.Float)
    wind_speed_condition = db.Column(db.String(50))
    weather_condition = db.Column(db.String(50))

    member = db.relationship('Member', back_populates='weather_preferences')

# 1 to many realtionship from Member to WeatherPreference. Each member can have mutliple preferences

class Member(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True) 
    password = db.Column(db.String(255)) 
    email = db.Column(db.String(150), unique=True) 
    city = db.Column(db.String(50))
    notifications = db.Column(db.Boolean, default=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    phone_number = db.Column(db.String(15), unique=True, nullable=True)
    weather_preferences = db.relationship('WeatherPreference', uselist=False, back_populates='member')
