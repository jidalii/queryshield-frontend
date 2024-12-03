import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import pytz

from components.analysis_history_component import analysis_history_component
from components.sidebar_login_component import sidebar_login_component
from utils.auth.jwt_token import decode_jwt_token, is_valid_analysis_detail_view_user
from utils.db.db_services import fetch_analyst_analysis_history
from configs.secrets import DATABASE_URL
from configs.configs import TIMEZONE

st.set_page_config("QueryShield", layout="wide")
st.title("Analysis History")
st.sidebar.title("QueryShield")

engine = create_engine(DATABASE_URL)

if "logined" not in st.session_state:
    st.session_state["logined"] = False

sidebar_login_component(engine)

ok, payload = decode_jwt_token(st.session_state["jwt_token"])
if not ok:
    st.error("Invalid Access.")
    st.stop()

uid = -1
if 'user' in payload and 'uid' in payload['user']:
    uid = payload['user']['uid']
if uid == -1:
    st.error("Invalid Access.")
    st.stop()

ok, uid = is_valid_analysis_detail_view_user(st.session_state["jwt_token"])
if not ok:
    st.error(uid)
    st.stop()

query_result = fetch_analyst_analysis_history(engine, uid)

processed_result = []
for analysis in query_result:
    # Convert time_created to Boston timezone and format it
    time_created = (
        analysis["time_created"].astimezone(TIMEZONE).strftime("%Y:%m:%d %H:%M")
    )

    # Create a dictionary with modified time_created
    processed_row = {
        "aid": analysis["aid"],
        "analysis_name": analysis["analysis_name"],
        # 'analyst_name': analysis['analyst_name'],
        # 'analyst_id': analysis['analyst_id'],
        "time_created": time_created,  # modified time_created
        "details": analysis["details"],
        "owners_count": analysis["owners_count"],
        "status": analysis["status"],
    }

    processed_result.append(processed_row)
test_df = pd.DataFrame(processed_result)

analysis_history_component(test_df)
