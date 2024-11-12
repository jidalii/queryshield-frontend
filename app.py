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
    
if "logged_in" in st.session_state:
    st.session_state["logged_in"]

# @st.dialog("Login")
def login():
    # with st.form("Login", border=False, clear_on_submit=True):
    user = UserLogin()
    user.email = st.text_input("Email", key="key1")
    user.password = st.text_input("Password", key="key2")
    if st.button("Log in"):
        # if st.form_submit_button("Log in"):
        login_handler(engine, user)
        st.session_state.logged_in = True
        print("here")
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
    if st.button("Log out"):
        st.session_state.logged_in = False
        st.session_state.pop("user")
        st.success("Logged out successfully.")
        st.rerun()

login_page = st.Page(login, title="Log in", icon=":material/login:")
signup_page = st.Page(signup, title="Sign up", icon=":material/login:")
logout_page = st.Page(logout, title="Log out", icon=":material/logout:")

analysis_history = st.Page(
    "webpages/analyst/Analysis History.py", title="Analysis History", icon=":material/history:", default=True
)
see_results = st.Page("webpages/analyst/See Results.py", title="See Results", icon=":material/bug_report:")
create_analysis = st.Page("webpages/analyst/Create_Analysis.py", title="Create Analysis", icon=":material/bug_report:")

analysis_catalog = st.Page(
    "webpages/data_owner/Analysis Catalog.py", title="Analysis Catalog", icon=":material/history:"
)
share_data = st.Page(
    "webpages/data_owner/Share Data.py", title="Share Data", icon=":material/notification_important:"
)

analysis_detail_view = st.Page("webpages/general/analysis_detail_view.py", title="Analysis Detail", icon=":material/history:")

analyst_page_config = {
    "Account": [logout_page],
    "Analyst": [create_analysis, analysis_history, see_results]
}

data_owner_page_config = {
    "Account": [logout_page],
    "Data Owner": [analysis_catalog, share_data]
}


if st.session_state.logged_in:
    print(st.session_state.get("logged_in"))
    username = st.session_state["user"]["first_name"]
    st.sidebar.write(f"Welcome, {username}!")
    # signout = st.sidebar.button("Signout", key="signout_button", icon=":material/logout:")
    pg = st.navigation(
        # data_owner_page_config
        analyst_page_config
    )
    # if signout:
    #     st.session_state["log_in"] = False
    #     st.session_state.pop("user")
    #     st.success("Logged out successfully.")
        # st.rerun()
else:
    print("not login:", st.session_state.get("logged_in"))
    pg = st.navigation([login_page, signup_page])
pg.run()
st.session_state["logged_in"]

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
