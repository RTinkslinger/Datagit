import sqlite3
import random
import requests
import json
import time
from flask import Flask, request, jsonify
from twilio.rest import Client
import os


app = Flask(__name__)

# Connect to the database
conn = sqlite3.connect('predictions.db')
cursor = conn.cursor()

# Create the predictions table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS predictions (
        phone_number TEXT PRIMARY KEY,
        prediction INTEGER,
        login_timestamp INTEGER
    )
''')

# CricAPI credentials
cricapi_key = "ede6ae5d-44c2-467c-b283-d95fe3612b81"


# Download the helper library from https://www.twilio.com/docs/python/install
import os
from twilio.rest import Client

# Set environment variables for your credentials
# Read more at http://twil.io/secure
account_sid = "AC5ae32679dfa70e656d7279f5f07b5c63"
auth_token = "f8be1128b78a12d109709e9528b960c9"
verify_sid = "VA0aa40b092e82884110b82d4f92e55b26"
verified_number = "+919820820663"

# Twilio client initialization
client = Client(account_sid, auth_token)

# Set the Twilio phone number
twilio_phone_number = "+919820820663"

# Function to generate OTP
def generate_otp():
    return random.randint(1000, 9999)

# Function to send OTP via Twilio
def send_otp(phone_number, otp):
    message = client.messages.create(
        body=f"Your OTP is: {otp}",
        from_=twilio_phone_number,
        to=phone_number
    )
    print(f"OTP: {otp} has been sent to {phone_number}")

# Function to validate the prediction
def validate_prediction(phone_number, prediction):
    cursor.execute('''
        SELECT prediction
        FROM predictions
        WHERE phone_number != ? AND (prediction = ? OR prediction = ? OR prediction = ?)
    ''', (phone_number, prediction, prediction + 3, prediction - 3))
    existing_predictions = cursor.fetchone()
    return existing_predictions is None

# Function to register a prediction
def register_prediction(phone_number, prediction):
    if validate_prediction(phone_number, prediction):
        cursor.execute('INSERT INTO predictions VALUES (?, ?, ?)', (phone_number, prediction, int(time.time())))
        conn.commit()
        return jsonify({'message': 'Prediction registered successfully!'})
    else:
        return jsonify({'error': 'Prediction is already taken. Please enter a new prediction.'}), 400

# Function to check if the user is logged in (within 24 hours)
def is_user_logged_in(phone_number):
    current_timestamp = int(time.time())
    cursor.execute('''
        SELECT login_timestamp
        FROM predictions
        WHERE phone_number = ?
    ''', (phone_number,))
    login_timestamp = cursor.fetchone()

    if login_timestamp is not None:
        if current_timestamp - login_timestamp[0] <= 24 * 60 * 60:
            return True

    return False

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    phone_number = data.get('phoneNumber')
    otp = data.get('otp')

    if is_user_logged_in(phone_number):
        return jsonify({'message': 'You are already logged in. You can continue using the service.'})
    else:
        stored_otp = generate_otp()
        send_otp(phone_number, stored_otp)  # Send the OTP to the entered phone number

        if otp == stored_otp:
            cursor.execute('INSERT OR REPLACE INTO predictions VALUES (?, NULL, ?)', (phone_number, int(time.time())))
            conn.commit()
            return jsonify({'message': 'Login successful. You can continue using the service.'})
        else:
            return jsonify({'error': 'Invalid OTP. Login failed.'}), 400

@app.route('/prediction', methods=['POST'])
def prediction():
    data = request.get_json()
    phone_number = data.get('phoneNumber')
    prediction = data.get('prediction')

    if is_user_logged_in(phone_number):
        return register_prediction(phone_number, prediction)
    else:
        return jsonify({'error': 'Please log in first.'}), 401

# Close the database connection
@app.teardown_appcontext
def close_connection(exception):
    conn.close()

if __name__ == '__main__':
    app.run()
