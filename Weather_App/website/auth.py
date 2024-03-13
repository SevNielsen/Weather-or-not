from flask import Blueprint, render_template, request, flash

auth = Blueprint('auth', __name__)

@auth.route('/login', methods = ['GET','POST'])
def login():
    data = request.form
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
        elif len(firstName) < 2 or len(lastName) < 2 or len(email) < 4 or len(password) < 2 or len(username) < 2:
            flash("Please provide enough characters and try again", category="error")
        else:
            flash("Account created successfully", category="success")

    return render_template("signup.html")

@auth.route('/dashboard')
def dashboard():
    return render_template("dashboard.html")

@auth.route('/navbar')
def navbar():
    return render_template("navbar.html")

