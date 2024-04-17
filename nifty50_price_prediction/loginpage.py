import streamlit as st
import sqlite3
import random
import string
from flask import Flask
from flask_mail import Mail, Message

app = Flask(__name__)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your_email@gmail.com'  # Replace with your email
app.config['MAIL_PASSWORD'] = 'your_password'  # Replace with your password
app.config['MAIL_DEBUG'] = True  # Enable debugging output
app.config['MAIL_DEFAULT_SENDER'] = 'your_email@gmail.com'  # Replace with your email

mail = Mail(app)

def create_users_table():
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS users1 (
                    id INTEGER PRIMARY KEY,
                    username TEXT UNIQUE,
                    password TEXT,
                    email TEXT UNIQUE,
                    verification_code TEXT,
                    email_verified INTEGER DEFAULT 0
                )''')

    cursor.execute("PRAGMA table_info(users)")
    print(cursor.fetchall())

    conn.commit()
    conn.close()

def generate_verification_code(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def send_verification_email(email, verification_code):
    with app.app_context():  # Use app context to send email
        msg = Message('Verify Your Email', recipients=[email])
        msg.body = f'Your verification code is: {verification_code}'
        mail.send(msg)

def register_user(username, password, email):
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users1 WHERE username=?", (username,))
    if cursor.fetchone() is not None:
        st.error("Username already exists. Please choose a different username.")
        conn.close()
        return False

    verification_code = generate_verification_code()
    send_verification_email(email, verification_code)

    cursor.execute("INSERT INTO users1 (username, password, email, verification_code) VALUES (?, ?, ?, ?)", (username, password, email, verification_code))
    conn.commit()
    conn.close()
    return True

def verify_email(username, verification_code):
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users1 WHERE username=? AND verification_code=?", (username, verification_code))
    user = cursor.fetchone()

    if user:
        cursor.execute("UPDATE users1 SET email_verified=1 WHERE username=?", (username,))
        conn.commit()
        st.success("Email verification successful!")
    else:
        st.error("Invalid verification code.")

    conn.close()

def login_user(username, password):
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users1 WHERE username=? AND password=? AND email_verified=1", (username, password))
    user = cursor.fetchone()

    conn.close()
    return user

def registration():
    st.title("Registration Page")

    new_username = st.text_input("New Username")
    new_password = st.text_input("New Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    email = st.text_input("Email")

    if st.button("Send Verification Code"):
        if new_password == confirm_password:
            if register_user(new_username, new_password, email):
                st.success("Verification code sent! Please check your email.")
            else:
                st.error("Failed to send verification code. Please try again.")
        else:
            st.error("Passwords do not match.")

    verification_code = st.text_input("Verification Code")
    if st.button("Verify Email"):
        # Verify the entered verification code
        verify_email(email, verification_code)

def registration():
    st.title("Registration Page")

    new_username = st.text_input("New Username")
    new_password = st.text_input("New Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    email = st.text_input("Email")

    if st.button("Register"):
        if new_password == confirm_password:
            if register_user(new_username, new_password, email):
                st.success("Registration successful! Please check your email for verification.")
            else:
                st.error("Failed to register. Please try again.")
        else:
            st.error("Passwords do not match.")

def verify_email_page():
    st.title("Email Verification")
    username = st.text_input("Username")
    verification_code = st.text_input("Verification Code")

    if st.button("Verify"):
        verify_email(username, verification_code)
        


def login():
    st.title("Nifty50 Stocks Price Prediction App ")
    st.image("https://nsearchives.nseindia.com/products/resources/images/nifty_50.jpg", width=200)

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username and password:
            user = authenticate_user(username, password)
            if user is not None:
                st.success(f"Welcome, {username}!")
                # Add your app logic or redirect to another page
                st.markdown("[Go to Main App Page](http://localhost:8502/)")
            else:
                st.error("Invalid username or password.")
        else:
            st.warning("Please enter both username and password.")

# Function to check user credentials in SQLite database
def authenticate_user(username, password):
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()

    # Check if username and password match in the database
    cursor.execute("SELECT * FROM users1 WHERE username=? AND password=?", (username, password))
    user = cursor.fetchone()

    conn.close()
    return user

def main():
    create_users_table()
    st.sidebar.title("Navigation")
    selection = st.sidebar.radio("Go to", ["Login", "Registration"])

    if selection == "Registration":
        registration()
        verify_email_page()
    elif selection == "Login":
        login()

if __name__ == "__main__":
    main()

