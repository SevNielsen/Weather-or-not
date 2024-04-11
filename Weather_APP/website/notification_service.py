# notification_service.py
from datetime import datetime, timedelta
from twilio.rest import Client
from flask import flash
from .models import Member, WeatherPreference
from .weather_utils import fetch_current_weather_data
import os

class NotificationService:
    def __init__(self, db_session):
        self.db_session = db_session
        self.load_twilio_config()

    def load_twilio_config(self):
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.twilio_number = os.getenv('TWILIO_NUMBER')
        self.client = Client(self.account_sid, self.auth_token)

    def send_sms(self, phone_number, message):
        try:
            message = self.client.messages.create(
                body=message,
                from_=self.twilio_number,
                to=phone_number
            )
            print(f"Sent message to {phone_number}")
        except Exception as e:
            flash(f"Failed to send SMS notification: {e}", category='error')

    def notify_users(self):
        members = self.db_session.query(Member).all()
        for member in members:
            if member.notifications and member.phone_number:
                current_weather = fetch_current_weather_data(member.city)
                if current_weather:
                    for preference in member.weather_preferences:
                        if self.weather_matches_preference(current_weather, preference) and \
                                self.can_notify(preference):
                            message = self.construct_message(current_weather, preference)
                            self.send_sms(member.phone_number, message)
                            self.update_last_notified(preference)

    def weather_matches_preference(self, weather_data, preference):
        # Temperature check
        if preference.condition_type == 'temperature':
            if preference.notify_when == 'above' and weather_data['temperature'] > preference.threshold_value:
                return True
            elif preference.notify_when == 'below' and weather_data['temperature'] < preference.threshold_value:
                return True

        # Wind speed check
        elif preference.condition_type == 'wind_speed':
            if preference.notify_when == 'above' and weather_data['wind_speed'] > preference.threshold_value:
                return True
            elif preference.notify_when == 'below' and weather_data['wind_speed'] < preference.threshold_value:
                return True

        elif preference.condition_type == 'general':
            if preference.notify_when == weather_data['weather_description'].lower():
                return True

        return False

    def construct_message(self, weather_data, preference):
        """ Construct the notification message based on the weather data and user preferences """
        base_message = f"Weather Alert for {weather_data['city']}: "

        if preference.condition_type == 'temperature':
            condition_message = f"Temperature is {'above' if preference.notify_when == 'above' else 'below'} {preference.threshold_value}°C, currently at {weather_data['temperature']}°C."
        elif preference.condition_type == 'wind_speed':
            condition_message = f"Wind speed is {'above' if preference.notify_when == 'above' else 'below'} {preference.threshold_value} km/h, currently at {weather_data['wind_speed']} km/h."
        elif preference.condition_type == 'general':
            condition_message = f"Current weather condition is {weather_data['weather_description'].capitalize()}, as per your preference."

        return base_message + condition_message
    
    def update_last_notified(self, preference):
        preference.last_notified = datetime.utcnow()
        self.db_session.commit()

    def can_notify(self, preference):
        if not preference.last_notified:
            return True
        # Notify once a day
        return datetime.utcnow() - preference.last_notified > timedelta(hours=24)
