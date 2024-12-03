import streamlit as st
import time

from models.auth import UserRegistration, UserLogin
from utils.auth.email_auth import login_handler, signup_handler

@st.dialog("Login")
def email_form(engine):
    with st.form("Login", border=False, clear_on_submit=True):
        user = UserLogin()
        user.email = st.text_input("Email", key="key1")
        user.password = st.text_input("Password", key="key2")
        submitted= st.form_submit_button("Log in")
        if submitted:
            isValid, err = login_handler(engine, user)
            if isValid:
                st.success("Login successful!")
                time.sleep(1)
                st.rerun()
            else:
                st.error(err)
                

@st.dialog("Signup")
def signup_form(engine):
    with st.form("Signup", border=False, clear_on_submit=True):
        newuser = UserRegistration()
        newuser.first_name = st.text_input("First Name", key="key1")
        newuser.last_name = st.text_input("Last Name", key="key2")
        newuser.email = st.text_input("Email", key="key3")
        newuser.password = st.text_input("Password", key="key4")
        newuser.role = st.radio("Role", options=["data_owner", "analyst"])
        if st.form_submit_button("Sign up"):
            isValid, err = signup_handler(engine, newuser)
            if isValid:
                st.success("Signup successful. Please go back and login!")
                time.sleep(1.5)
                st.rerun()
            else:
                st.error(err)


def sidebar_login_component(engine):
    if st.session_state.get("logined"):
        username = st.session_state["user"]["first_name"]
        st.sidebar.write(f"Welcome, {username}!")
        signout = st.sidebar.button("Signout", key="signout_button")
        if signout:
            st.session_state["logined"] = False
            st.session_state.pop("user")
            st.success("Logged out successfully.")
            time.sleep(1)
            st.rerun()
    else:
        login = st.sidebar.button("Login", key="login_button")
        signup = st.sidebar.button("Signup", key="signup_button")
        if login:
            email_form(engine)

        if signup:
            signup_form(engine)
            
        # # DEBUG: Display user session if exists
        # if "user" in st.session_state:
        #     st.session_state["user"]