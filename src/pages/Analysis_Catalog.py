import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

from components.analysis_catalog_component import analysis_catalog_component
from utils.db.db_services import fetch_all_analysis_catalog
from components.sidebar_login_component import (
    sidebar_login_component,
)
from configs.secrets import DATABASE_URL
from configs.configs import TIMEZONE
from utils.auth.jwt_token import is_valid_data_owner

st.set_page_config("QueryShield", layout="wide")

st.title("Analysis Catalog")
st.sidebar.title("QueryShield")

ok, uid = is_valid_data_owner(st.session_state["jwt_token"])
if not ok:
    st.error("Invalid token. Please login again.")
    st.stop()

engine = create_engine(DATABASE_URL)

if "logined" not in st.session_state:
    st.session_state["logined"] = False

sidebar_login_component(engine)

# Convert the dictionary into a Pandas DataFrame
query_result = fetch_all_analysis_catalog(engine)
column_names = list(query_result[0].keys())

processed_result = []
for analysis in query_result:
    # Convert time_created to Boston timezone and format it
    time_created = (
        analysis["time_created"].astimezone(TIMEZONE).strftime("%Y-%m-%d %H:%M")
    )
    # Create a dictionary with modified time_created
    processed_row = {
        "aid": analysis["aid"],
        "jwt": st.session_state["jwt_token"],
        "analysis_name": analysis["analysis_name"],
        "analyst_name": analysis["analyst_name"],
        "analyst_id": analysis["analyst_id"],
        "time_created": time_created,
        "details": analysis["details"],
        "status": analysis["status"],
        "owners_count": analysis["owners_count"],
    }

    processed_result.append(processed_row)

df = pd.DataFrame(processed_result)

analysis_catalog_component(df)
