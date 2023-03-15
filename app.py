from flask import Flask, request, url_for, redirect, render_template, session
# Imported Classes
from routes.authentication import Authentication

# Blueprints for Flask routes
from routes.transaction import increment_balance_blueprint

# Configure App
app = Flask(__name__) 

# Declare blueprints
app.register_blueprint(increment_balance_blueprint)

users = {}

investments = 1000.00
balance = 5000.00

# Session key
app.secret_key = '406-trades'

# Login Redirect Everytime User Opens The Website
@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('home'))
    else:
        return redirect(url_for('create'))

# Login Page Form
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username] == password:
            session['username'] = username
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error='Invalid username or password')
    else:
        return render_template('login.html')

# Create Account Page
@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        passwordTwo = request.form['passwordTwo']
        auth = Authentication(username, password, passwordTwo)
        if auth.valid_create():
            if username in users:
                return render_template('create.html', error='Username already exists')
            else:
                users[username] = password
                return redirect(url_for('login'))
        else:
            return render_template('create.html', error='Invalid Username or Password')
    else:
        return render_template('create.html')

# Home Page
@app.route("/home") 
def home():
    return render_template('home.html', username=session['username'], i=investments, b=balance)

# Stock Market Page
@app.route("/market") 
def market():
    return render_template('market.html')

# FAQ Page
@app.route("/faq") 
def faq():
    return render_template('faq.html')

# Account Profile Page
@app.route("/account") 
def account():
    return render_template('account.html')

# Removes Session When User Logs Out
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run()