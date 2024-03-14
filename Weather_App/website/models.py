from . import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.)
    password = db.Column()
    email = db.Column()
    city = db.Column()
    
