from flask import Blueprint, render_template

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    return render_template("login.html")


@auth.route('/logout')
def logout():
    return "<p>Logout</p>"


@auth.route('/signup')
def sign_up():
    return render_template("signup.html")

@auth.route('/dashboard')
def dashboard():
    return render_template("dashboard.html")

@auth.route('/navbar')
def navbar():
    return render_template("navbar.html")

