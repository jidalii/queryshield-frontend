from sqlalchemy import create_engine
import pytz

import streamlit as st
from streamlit.components.v1 import html

from components.analysis_detail.analysis_description_component import (
    view_threat_model_component,
    view_analysis_details_component,
)
from components.analysis_detail.schema_table_component import schema_table_component
from db.db_services import fetch_single_analysis
from utils.helpers import convert_dict_to_df, convert_dict_to_category_dict
from utils.row_detection import fake_click
from configs.configs import SCHEMA_TYPES
from configs.html import HTML_CONTENTS
from configs.secrets import DATABASE_URL

st.set_page_config("Analysis Detail View", layout="wide")

if "aid" not in st.query_params:
    st.error("Request ID should be provided.")
    st.stop()
else:
    st.session_state["analysis_id_view"] = st.query_params.aid
    st.write("analysis id: ", st.session_state["analysis_id_view"])

st.title("Analysis Detail View")

with st.sidebar:
    st.empty()

engine = create_engine(DATABASE_URL)

if "view_category_df" not in st.session_state:
    st.session_state["view_category_df"] = {}

if "cell_position" not in st.session_state:
    st.session_state["cell_position"] = (0, 0)

analysis = fetch_single_analysis(engine, st.query_params["aid"])
boston_tz = pytz.timezone("America/New_York")
time_created = analysis["time_created"].astimezone(boston_tz).strftime("%Y:%m:%d %H:%M")

# Create a dictionary with modified time_created
analysis_details = {
    "aid": analysis["aid"],
    "analysis_name": analysis["analysis_name"],
    "time_created": time_created,
    "details": analysis["details"],
    "status": analysis["status"],
}
data = analysis_details["details"]
raw_schema = data["schema"]
schema = convert_dict_to_df(raw_schema)
category_df = convert_dict_to_category_dict(raw_schema)


schema_table_component(schema, SCHEMA_TYPES, category_df)

view_threat_model_component(data)

view_analysis_details_component(data)

st.button("", key="fakeButton", on_click=fake_click, type="primary")
st.markdown(
    """
    <style>
    div[data-testid="stTextInput"][data-st-key="CELL_ID"] {
        visibility: hidden;
    }
    button[kind="primary"] {
        visibility: hidden;
    }
    button {
        height: 0px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
html(HTML_CONTENTS)
