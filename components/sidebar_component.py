import streamlit as st
from sqlalchemy import create_engine

from models.auth import UserRegistration, UserLogin
from utils.auth.email_auth import login_handler, signup_handler

engine = create_engine(
    "postgresql+psycopg2://user1:12345678!@localhost:5432/queryshield"
)

# @st.dialog("Login")
def login():
    with st.form("Login", border=False, clear_on_submit=True):
        user = UserLogin()
        user.email = st.text_input("Email", key="key1")
        user.password = st.text_input("Password", key="key2")
        if st.form_submit_button("Log in"):
            login_handler(engine, user)
            st.rerun()


# @st.dialog("Signup")
def signup():
    with st.form("Signup", border=False, clear_on_submit=True):
        newuser = UserRegistration()
        newuser.first_name = st.text_input("First Name", key="key1")
        newuser.last_name = st.text_input("Last Name", key="key2")
        newuser.email = st.text_input("Email", key="key3")
        newuser.password = st.text_input("Password", key="key4")
        newuser.role = st.radio("Role", options=["data_owner", "analyst"])
        if st.form_submit_button("Sign up"):
            signup_handler(engine, newuser)

def logout():
    st.session_state["logined"] = False
    st.session_state.pop("user")
    st.success("Logged out successfully.")
    st.rerun()

login_page = st.Page(login, title="Log in", icon=":material/login:")
signup_page = st.Page(signup, title="Log in", icon=":material/login:")
logout_page = st.Page(logout, title="Log out", icon=":material/logout:")

create_analysis = st.Page(
    "webpages/analyst/Create_Analysis.py", title="Create Analysis", icon=":material/history:", default=True
)
analysis_history = st.Page(
    "webpages/analyst/Analysis History.py", title="Analysis History", icon=":material/history:", default=True
)
see_results = st.Page("webpages/analyst/See Results.py", title="See Results", icon=":material/bug_report:")

analysis_catalog = st.Page(
    "webpages/data_owner/Analysis Catalog.py", title="Analysis Catalog", icon=":material/history:"
)
share_data = st.Page(
    "webpages/data_owner/Share Data.py", title="Share Data", icon=":material/notification_important:"
)

analysis_detail_view = st.Page("webpages/general/analysis_detail_view.py", title="Analysis Detail", icon=":material/history:")

analyst_page_config = {
    "Account": [logout_page],
    "Analyst": [analysis_history, see_results]
}

data_owner_page_config = {
    "Account": [logout_page],
    "Data Owner": [analysis_catalog, share_data]
}

def sidebar_login_component(engine):
    if st.session_state.get("logined"):
        username = st.session_state["user"]["first_name"]
        st.sidebar.write(f"Welcome, {username}!")
        signout = st.sidebar.button("Signout", key="signout_button", icon=":material/logout:")
        pg = st.navigation(
            data_owner_page_config
        )
        if signout:
            st.session_state["logined"] = False
            st.session_state.pop("user")
            st.success("Logged out successfully.")
            st.rerun()
    else:
        pg = st.navigation([login_page, signup_page])
        # login = st.sidebar.button("Log in", key="login_button", icon=":material/login:")
        # signup = st.sidebar.button("Sign up", key="signup_button")
        # if login:
        #     login(engine)

        # if signup:
        #     signup(engine)
            
        # DEBUG: Display user session if exists
        if "user" in st.session_state:
            st.session_state["user"]
    pg.run()