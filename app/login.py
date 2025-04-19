import streamlit as st
import json

def load_user_data():
    # Load the user data from a JSON file
    with open("app/users.json") as f:
        return json.load(f)

def check_credentials(username, password):
    users = load_user_data()
    for user in users["users"]:
        if user["username"] == username:
            # Here we are comparing plain text password, but you should hash the passwords in a real app
            if user["password"] == password:
                return user
    return None

def login():
    st.title("Login to EchoDeepak")

    # Login form
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = check_credentials(username, password)
        if user:
            st.session_state.user = user
            st.session_state.logged_in = True
            st.success(f"Logged in as {username}")
            return user
        else:
            st.error("Invalid credentials, please try again.")
            return None
    return None