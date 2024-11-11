from multiprocessing.shared_memory import SharedMemory

from sqlalchemy import create_engine
import pytz

import streamlit as st
from streamlit.components.v1 import html

from components.analysis_description_component import *
from components.schema_table_component import schema_table_component
from utils.db.db_services import fetch_single_analysis
from utils.helpers import convert_dict_to_df, convert_dict_to_category_dict
from utils.row_detection import *
from configs.configs import schema_types
from configs.html import html_contents

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

engine = create_engine(
    "postgresql+psycopg2://user1:12345678!@localhost:5432/queryshield"
)

if "view_category_df" not in st.session_state:
    st.session_state['view_category_df'] ={}

if "cell_position" not in st.session_state:
    st.session_state["cell_position"] = (0, 0)

analysis = fetch_single_analysis(engine, st.query_params["aid"])
boston_tz = pytz.timezone('America/New_York')
time_created = analysis['time_created'].astimezone(boston_tz).strftime('%Y:%m:%d %H:%M')

# Create a dictionary with modified time_created
analysis_details = {
    'aid': analysis['aid'],
    'analysis_name': analysis['analysis_name'],
    'time_created': time_created,
    'details': analysis['details'],
    'status': analysis['status'],
}
data = analysis_details['details']
raw_schema = data['schema']
schema = convert_dict_to_df(raw_schema)
category_df = convert_dict_to_category_dict(raw_schema)


schema_table_component(schema, schema_types, category_df)

view_threat_model(data)

view_analysis_details(data)

if "query_name" in st.session_state:
    st.subheader("Data Schema")
    if "user_input" in st.session_state:
        schema_table_component()
        
        
    st.subheader("Threat Model")
    st.markdown(f"- {st.session_state.threat_model}")
    st.markdown("#### Cloud Provider:")
    cloud_providers = ["Google Cloud", "Microsoft Azure", "Cloud 1"]
    for provider in cloud_providers:
        st.markdown("- " + provider)
    st.subheader("Analysis Details")
    if "query_name" in st.session_state:
        st.markdown("#### Query Name:")
        st.write(f"{st.session_state.query_name}")
    if "query" in st.session_state:
        st.markdown("#### Query:")
        st.code(st.session_state.query)
    if "description" in st.session_state:
        st.markdown("#### Description:")
        st.write(f"{st.session_state.description}")

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
html(html_contents)