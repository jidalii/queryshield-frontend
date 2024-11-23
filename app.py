import asyncio
import streamlit as st

from sqlalchemy import create_engine


from models.analysis import *
from utils.db.schema_validation import *
from utils.db.db_services import *
from utils.row_detection import CustomServer
import streamlit as st
from sqlalchemy import create_engine

from models.auth import UserRegistration, UserLogin
from utils.auth.email_auth import login_handler, signup_handler

engine = create_engine(
    "postgresql+psycopg2://user1:12345678!@localhost:5432/queryshield"
)


st.set_page_config("QueryShield", layout="wide")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# if "aid" in st.query_params:
#     st.session_state.logged_in = True
# if "logged_in" in st.session_state:
#     st.session_state["logged_in"]



def login():
    user = UserLogin()
    user.email = st.text_input("Email", key="key1")
    user.password = st.text_input("Password", key="key2")
    if st.button("Log in"):
        user, err = login_handler(engine, user)
        if not user:
            st.error(err)
        else:
            st.session_state["user"] = user
            st.session_state["logged_in"] = True
        st.rerun()


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
    if st.button("Log out"):
        st.session_state.logged_in = False
        st.session_state.pop("user")
        st.success("Logged out successfully.")
        st.rerun()


# login_page = st.Page(login, title="Log in", icon=":material/login:", default=True)


def logout():
    st.title("Log out")
    if st.button("Log out"):
        st.session_state.logged_in = False
        st.experimental_rerun()


login_page = st.Page(login, title="Log in", icon=":material/login:")
signup_page = st.Page(signup, title="Sign up", icon=":material/login:")
# logout_page = st.Page(logout, title="Log out", icon=":material/logout:", default=False)
logout_page = st.Page(logout, title="Log out", icon=":material/logout:")

analysis_history = st.Page(
    "webpages/analysis_history.py", title="Analysis History", icon=":material/history:"
)
see_results = st.Page(
    "webpages/see_results.py", title="See Results", icon=":material/bug_report:"
)
create_analysis = st.Page(
    "webpages/create_analysis.py",
    title="Create Analysis",
    icon=":material/bug_report:",
    # default=True,
)

analysis_catalog = st.Page(
    "webpages/Analysis Catalog.py",
    title="Analysis Catalog",
    icon=":material/history:",
    # default=True,
)
share_data = st.Page(
    "webpages/Share Data.py",
    title="Share Data",
    icon=":material/notification_important:",
)

analysis_detail_view = st.Page(
    "webpages/analysis_Detail_View.py",
    title="Analysis Detail",
    icon=":material/history:",
)

analyst_page_config = {
    "Account": [logout_page],
    "Analyst": [create_analysis, analysis_history, see_results],
}

data_owner_page_config = {
    "Account": [logout_page],
    "Data Owner": [analysis_catalog, share_data],
}


if st.session_state.logged_in:
    username = st.session_state["user"]["first_name"]
    st.sidebar.write(f"Welcome, {username}!")
    if st.session_state["user"]["role"] == "data_owner":
        pg = st.navigation(data_owner_page_config)
    else:
        pg = st.navigation(analyst_page_config)
    pg.run()
else:
    # login_page()
    login()
    pg = st.navigation([login_page, signup_page])
    pg.run()

if __name__ == "__main__":
    import streamlit.web.bootstrap

    if "__streamlitmagic__" not in locals():
        # Code adapted from bootstrap.py in streamlit
        streamlit.web.bootstrap._fix_sys_path(__file__)
        streamlit.web.bootstrap._fix_tornado_crash()
        streamlit.web.bootstrap._fix_sys_argv(__file__, [])
        streamlit.web.bootstrap._fix_pydeck_mapbox_api_warning()
        # streamlit.web.bootstrap._fix_pydantic_duplicate_validators_error()

        server = CustomServer(__file__, is_hello=False)

        async def run_server():
            await server.start()
            streamlit.web.bootstrap._on_server_start(server)
            streamlit.web.bootstrap._set_up_signal_handler(server)
            await server.stopped

        asyncio.run(run_server())
