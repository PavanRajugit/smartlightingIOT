from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import requests
import smtplib
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
app.secret_key = 'your_secret_key'

DEFAULT_USERNAME = 'admin'
DEFAULT_PASSWORD = 'admin'


def send_email(subject, body, to_email):
    smtp_server = "smtp.gmail.com"
    port = 465
    sender_email = "notifysunilkumar@gmail.com"  # Replace with your Gmail address
    sender_password = "bycrcxxeuqzlgqzs"  # Replace with your App Password or Gmail password

    message = MIMEMultipart()
    message["From"] = sender_email
    message["notifysunilkumar@gmail.com"] = to_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    with smtplib.SMTP_SSL(smtp_server, port) as server:
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, message.as_string())

    with smtplib.SMTP_SSL(smtp_server, port) as server:
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, message.as_string())

# Function to generate random location
def generate_random_location():
    latitude = round(random.uniform(-90, 90), 4)
    longitude = round(random.uniform(-180, 180), 4)
    return f"Latitude: {latitude}, Longitude: {longitude}"


def get_thingspeak_data():
    url = "https://api.thingspeak.com/channels/2522994/feeds.json?results=1"
    response = requests.get(url)
    data = response.json()
    return data


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == DEFAULT_USERNAME and password == DEFAULT_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('index.html'))
        else:
            return render_template('login.html', error='Invalid username or password')

    return render_template('login', error=None)

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/')
def index():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    data = get_thingspeak_data()
    channel = data['channel']
    feeds = data['feeds'][0]
    
    
    ir_value = feeds['field6']
    alert = ""
    alert_color = ""
    location_details = ""

    if ir_value == "0":
        alert = "Lights are glowing"
        alert_color = "green"
    elif ir_value == "1":
        alert = "Lights are not glowing"
        alert_color = "red"
    elif ir_value is None:
        alert = "Lights are not functioning"
        alert_color = "red"
        
        
        location_details = generate_random_location()
        
        subject = "Alert: Lights Not Functioning"
        body = f"The lights are not functioning. Please check.\nLocation Details: {location_details}"
        to_email = "503badgateway@gmail.com"  
        send_email(subject, body, to_email)

    return render_template('features.html', channel=channel, feeds=feeds, alert=alert, alert_color=alert_color, location_details=location_details)

if __name__ == '__main__':
    app.run(debug=True)
