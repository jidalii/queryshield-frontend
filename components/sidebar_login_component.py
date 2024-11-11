import streamlit as st

from models.auth import UserRegistration, UserLogin
from utils.auth.email_auth import login_handler, signup_handler

@st.dialog("Login")
def email_form(engine):
    with st.form("Login", border=False, clear_on_submit=True):
        user = UserLogin()
        user.email = st.text_input("Email", key="key1")
        user.password = st.text_input("Password", key="key2")
        if st.form_submit_button("Log in"):
            login_handler(engine, user)
            st.rerun()


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
            signup_handler(engine, newuser)


def sidebar_login_component(engine):
    if st.session_state.get("logined"):
        username = st.session_state["user"]["first_name"]
        st.sidebar.write(f"Welcome, {username}!")
        signout = st.sidebar.button("Signout", key="signout_button")
        if signout:
            st.session_state["logined"] = False
            st.session_state.pop("user")
            st.success("Logged out successfully.")
            st.rerun()
    else:
        login = st.sidebar.button("Login", key="login_button")
        signup = st.sidebar.button("Signup", key="signup_button")
        if login:
            email_form(engine)

        if signup:
            signup_form(engine)
            
        # DEBUG: Display user session if exists
        if "user" in st.session_state:
            st.session_state["user"]