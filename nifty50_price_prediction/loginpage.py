import streamlit as st
import sqlite3

# Create the users table if it doesn't exist
def create_users_table():
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    username TEXT UNIQUE,
                    password TEXT
                )''')

    conn.commit()
    conn.close()

# Function to check user credentials in SQLite database
def authenticate_user(username, password):
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()

    # Check if username and password match in the database
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = cursor.fetchone()

    conn.close()
    return user

def login():
    st.title("Login Page")

    # Input fields for username and password
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    # Login button
    if st.button("Login"):
        user = authenticate_user(username, password)
        if user is not None:
            st.success(f"Welcome, {username}!")
            # Add your app logic or redirect to another page
        else:
            st.error("Invalid username or password.")

def register_user(username, password):
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()

    # Check if username already exists
    cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    if cursor.fetchone() is not None:
        st.error("Username already exists. Please choose a different username.")
        conn.close()
        return False

    # Add new user to database
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    conn.commit()
    conn.close()
    return True

def registration():
    st.title("Registration Page")

    # Input fields for registration
    new_username = st.text_input("New Username")
    new_password = st.text_input("New Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    # Register button
    if st.button("Register"):
        if new_password == confirm_password:
            if register_user(new_username, new_password):
                st.success("Registration successful!")
            else:
                st.error("Failed to register. Please try again.")
        else:
            st.error("Passwords do not match.")

def main():
    create_users_table()  # Create the users table when the app starts
    st.sidebar.title("Navigation")
    selection = st.sidebar.radio("Go to", ["Login", "Registration"])

    if selection == "Login":
        login()
    elif selection == "Registration":
        registration()

if __name__ == "__main__":
    main()

