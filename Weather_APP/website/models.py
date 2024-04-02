from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

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
