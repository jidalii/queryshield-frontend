# Imports
import streamlit as st
import pandas as pd
import pytz
from sqlalchemy import create_engine
from components.sidebar_login_component import sidebar_login_component
from utils.row_detection import *
from utils.helpers import (
    convert_dict_to_df,
    convert_dict_to_category_dict,
    fetch_name_and_type_tuple,
)
from utils.db.db_services import (
    fetch_single_analysis,
    register_data_owner,
    is_registered_owner,
)
from utils.share_data_validation import validate_share_data_file
import streamlit.components.v1 as components

_my_component = components.declare_component(
    "my_component",  # Name of the component (matches frontend's name)
    path="./component-template/template/my_component/frontend/build",  # Adjust path to your build folder
)


# Constants
DATABASE_URL = "postgresql+psycopg2://user1:12345678!@localhost:5432/queryshield"
TIMEZONE = pytz.timezone("America/New_York")

# Streamlit Page Configuration
st.set_page_config(page_title="QueryShield", layout="wide", initial_sidebar_state="expanded")
st.title("Share Data")
st.sidebar.title("QueryShield")

# Database Engine Initialization
engine = create_engine(DATABASE_URL)
sidebar_login_component(engine)

# Session State Initialization
def initialize_session_state():
    if "view_category_df" not in st.session_state:
        st.session_state["view_category_df"] = {}
    if "cell_position" not in st.session_state:
        st.session_state["cell_position"] = (0, 0)
    if "data_to_share" not in st.session_state:
        st.session_state["data_to_share"] = pd.DataFrame(columns=names)

# Fetch and Format Analysis Data
def fetch_analysis_data():
    analysis = fetch_single_analysis(engine, st.query_params["aid"])
    time_created = analysis["time_created"].astimezone(TIMEZONE).strftime("%Y:%m:%d %H:%M")
    return {
        "aid": analysis["aid"],
        "analysis_name": analysis["analysis_name"],
        "time_created": time_created,
        "details": analysis["details"],
        "status": analysis["status"],
    }

analysis_details = fetch_analysis_data()
raw_schema = analysis_details["details"]["schema"]
schema = convert_dict_to_df(raw_schema)
category_dict = convert_dict_to_category_dict(raw_schema)
names, dtypes = fetch_name_and_type_tuple(raw_schema)
table_headers = [f"{name} ({dtype})" for name, dtype in zip(names, dtypes)]

df_to_share = pd.DataFrame(columns=names)


initialize_session_state()

# File Upload
st.markdown("<h3 style='text-align: center; color:black;'>Upload as CSV or Enter Data Here</h3>", unsafe_allow_html=True)
uploaded_file = st.file_uploader("", label_visibility="collapsed", type="csv")
if uploaded_file is not None:
    st.session_state["data_to_share"] = pd.read_csv(uploaded_file)
    df_to_share = st.session_state["data_to_share"]
    print("file uploaded")

# Column Configuration for Data Editor
def construct_column_config_share_data(df, table_headers, names, dtypes, category_dict):
    column_config = {}
    for i, (header, name, dtype) in enumerate(zip(table_headers, names, dtypes)):
        if dtype == "Category":
            if name in df:
                df[name] = df[name].astype(str)
            column_config[name] = st.column_config.SelectboxColumn(
                label=header,
                options=[str(option) for option in category_dict[i]],
                default=str(category_dict[i][0]),
            )
        elif dtype in ["Integer", "Float"]:
            column_config[name] = st.column_config.NumberColumn(label=header)
        else:
            column_config[name] = st.column_config.TextColumn(label=header)
    return column_config

column_config = construct_column_config_share_data(
    st.session_state["data_to_share"], table_headers, names, dtypes, category_dict
)

# Data Editor
st.session_state["data_to_share"] = st.data_editor(
    df_to_share,
    column_config=column_config,
    num_rows="dynamic",
    hide_index=True,
    use_container_width=True,
)

data_dict = st.session_state["data_to_share"].to_dict(orient="list")
replication_factor = 3

def my_component(data, schema, replication_factor, key=None):
    """
    Wrapper for the custom Streamlit component.

    Args:
        data (dict): Data to be secret shared.
        schema (list): Table schema (list of column names).
        replication_factor (int): Replication factor for secret sharing.
        key (str): Unique key for the Streamlit component instance.

    Returns:
        Any: The result from the component.
    """
    return _my_component(
        data={"data": data, "schema": schema}, replication_factor=replication_factor, key=key
    )


# Data Submission
def handle_submission():
    is_valid, err = validate_share_data_file(st.session_state["data_to_share"], names, dtypes)
    if is_valid:
        aid = st.query_params["aid"]
        uid = st.query_params["uid"]
        if is_registered_owner(engine, aid, uid):
            st.error("Error: you have already registered for this analysis")
        else:
            success, err = register_data_owner(engine, aid, uid)
            if success:
                outputs = my_component(data_dict, names, replication_factor)
                print(outputs)
                st.success("Success")
            else:
                st.error(f"Error: {err}")
    else:
        st.error(f"Error: {err}")


if st.button("Secret Share Data"):
    handle_submission()
