from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import Member
from werkzeug.security import generate_password_hash, check_password_hash
from . import db 

auth = Blueprint('auth', __name__)

@auth.route('/login', methods = ['GET','POST'])
def login():
    #data = request.form
    return render_template("login.html")


@auth.route('/logout')
def logout():
    return "<p>Logout</p>"


@auth.route('/signup', methods = ['GET','POST'])
def sign_up():
    if request.method == 'POST':
        firstName = request.form.get('First_Name')
        lastName = request.form.get('Last_Name')
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
    
        if firstName is None or lastName is None or email is None or password is None or username is None:
            flash("Please revise your information and try again", category="error")
        elif len(firstName) < 2 or len(lastName) < 2 or len(email) < 10 or len(password) < 2 or len(username) < 2:
            flash("Please provide enough characters and try again", category="error")
        else:
            member = Member(username = username, first_name = firstName, last_name = lastName, email = email, password=generate_password_hash(password, method='pbkdf2:sha256'))
            db.session.add(member)
            db.session.commit()
            flash("Account created successfully", category="success")
            return redirect(url_for('auth.profile'))

    return render_template("signup.html")

@auth.route('/dashboard')
def dashboard():
    return render_template("dashboard.html")

@auth.route('/navbar')
def navbar():
    return render_template("navbar.html")

@auth.route('/profile')
def profile():
    return render_template("profile.html")

