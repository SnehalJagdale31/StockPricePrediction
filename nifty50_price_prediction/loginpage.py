import streamlit as st
import sqlite3
import random
import string
from flask import Flask
from flask_mail import Mail, Message

# Flask app initialization
app = Flask(__name__)

# Flask-Mail configuration for sending emails
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'enter your mail id'  # Your email address
app.config['MAIL_PASSWORD'] = 'enter you pass key'          # App-specific password
app.config['MAIL_DEBUG'] = True  # Enable debugging for email
app.config['MAIL_DEFAULT_SENDER'] = 'snehaljagdale186@gmail.com'  # Default sender email

mail = Mail(app)  # Initialize Flask-Mail

# Function to create a SQLite database table for storing user data
def create_users_table():
    conn = sqlite3.connect('user_data.db')  # Connect to the SQLite database
    cursor = conn.cursor()

    # Create the 'users1' table if it doesn't already exist
    cursor.execute('''CREATE TABLE IF NOT EXISTS users1 (
                    id INTEGER PRIMARY KEY,
                    username TEXT UNIQUE,
                    password TEXT,
                    email TEXT UNIQUE,
                    verification_code TEXT,
                    email_verified INTEGER DEFAULT 0
                )''')

    cursor.execute("PRAGMA table_info(users1)")  # Display table schema
    print(cursor.fetchall())

    conn.commit()  # Save changes
    conn.close()   # Close the database connection

# Function to generate a random verification code
def generate_verification_code(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

# Function to send a verification email to the user
def send_verification_email(email, verification_code):
    with app.app_context():  # Ensure we are in the app context
        msg = Message('Verify Your Email', recipients=[email])  # Email subject and recipient
        msg.body = f'Your verification code is: {verification_code}'  # Email body
        mail.send(msg)  # Send the email

# Function to register a new user
def register_user(username, password, email):
    conn = sqlite3.connect('user_data.db')  # Connect to the SQLite database
    cursor = conn.cursor()

    # Check if the username already exists
    cursor.execute("SELECT * FROM users1 WHERE username=?", (username,))
    if cursor.fetchone() is not None:
        st.error("Username already exists. Please choose a different username.")
        conn.close()
        return False

    # Generate and send verification code
    verification_code = generate_verification_code()
    send_verification_email(email, verification_code)

    # Insert the new user into the database
    cursor.execute("INSERT INTO users1 (username, password, email, verification_code) VALUES (?, ?, ?, ?)", 
                   (username, password, email, verification_code))
    conn.commit()
    conn.close()
    return True

# Function to verify the user's email using the verification code
def verify_email(username, verification_code):
    conn = sqlite3.connect('user_data.db')  # Connect to the SQLite database
    cursor = conn.cursor()

    # Check if the verification code matches the user's record
    cursor.execute("SELECT * FROM users1 WHERE username=? AND verification_code=?", (username, verification_code))
    user = cursor.fetchone()

    if user:
        # Update the email_verified status in the database
        cursor.execute("UPDATE users1 SET email_verified=1 WHERE username=?", (username,))
        conn.commit()
        st.success("Email verification successful!")
    else:
        st.error("Invalid verification code.")

    conn.close()

# Function to log in the user
def login_user(username, password):
    conn = sqlite3.connect('user_data.db')  # Connect to the SQLite database
    cursor = conn.cursor()

    # Check if username, password, and email_verified flag match
    cursor.execute("SELECT * FROM users1 WHERE username=? AND password=? AND email_verified=1", (username, password))
    user = cursor.fetchone()

    conn.close()
    return user

# Registration page logic
def registration():
    st.title("Registration Page")

    # Input fields for user details
    new_username = st.text_input("New Username")
    new_password = st.text_input("New Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    email = st.text_input("Email")

    if st.button("Send Verification Code"):
        if new_password == confirm_password:  # Check if passwords match
            if register_user(new_username, new_password, email):
                st.success("Verification code sent! Please check your email.")
            else:
                st.error("Failed to send verification code. Please try again.")
        else:
            st.error("Passwords do not match.")

# Email verification page logic
def verify_email_page():
    st.title("Email Verification")
    username = st.text_input("Username")
    verification_code = st.text_input("Verification Code")

    if st.button("Verify"):
        verify_email(username, verification_code)

# Login page logic
def login():
    st.title("Nifty50 Stocks Price Prediction App")
    st.image("https://nsearchives.nseindia.com/products/resources/images/nifty_50.jpg", width=200)

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username and password:
            user = authenticate_user(username, password)
            if user is not None:
                st.success(f"Welcome, {username}!")
                # Redirect to the main app page
                st.markdown("[Go to Main App Page](http://15.206.66.31:8502)")
            else:
                st.error("Invalid username or password.")
        else:
            st.warning("Please enter both username and password.")

# Function to authenticate user credentials
def authenticate_user(username, password):
    conn = sqlite3.connect('user_data.db')  # Connect to the SQLite database
    cursor = conn.cursor()

    # Check if the credentials match an entry in the database
    cursor.execute("SELECT * FROM users1 WHERE username=? AND password=?", (username, password))
    user = cursor.fetchone()

    conn.close()
    return user

# Main function for app navigation
def main():
    create_users_table()  # Create the database table if it doesn't exist
    st.sidebar.title("Navigation")
    selection = st.sidebar.radio("Go to", ["Login", "Registration"])  # Navigation options

    if selection == "Registration":
        registration()
        verify_email_page()
    elif selection == "Login":
        login()

# Entry point for the app
if __name__ == "__main__":
    main()
