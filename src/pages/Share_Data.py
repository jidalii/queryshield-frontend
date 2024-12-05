import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from components.sidebar_login_component import sidebar_login_component
from components.share_data.secret_share_component import secret_share_component
from utils.helpers import (
    convert_dict_to_df,
    convert_dict_to_category_dict,
    fetch_name_and_type_tuple,
)
import utils.share_data_helper as share_data_helper
from configs.secrets import DATABASE_URL


# Streamlit Page Configuration
st.set_page_config(
    page_title="QueryShield", layout="wide", initial_sidebar_state="expanded"
)
st.title("Share Data")
st.sidebar.title("QueryShield")

share_data_helper.check_query_params()
share_data_helper.initialize_user()

# Database Engine Initialization
engine = create_engine(DATABASE_URL)
sidebar_login_component(engine)

# Fetch and Format Analysis Data

analysis_details = share_data_helper.fetch_analysis_data(engine)
raw_schema = analysis_details["details"]["schema"]
schema = convert_dict_to_df(raw_schema)
threat_model = analysis_details["details"]["threat_model"]
category_dict = convert_dict_to_category_dict(raw_schema)
names, dtypes = fetch_name_and_type_tuple(raw_schema)
table_headers = [f"{name} ({dtype})" for name, dtype in zip(names, dtypes)]

replication_factor = -1
if threat_model == "Malicious":
    replication_factor = 4
elif threat_model == "Semi-Honest":
    replication_factor = 3

df_to_share = pd.DataFrame(columns=names)
share_data_helper.initialize_session_state(names)


# File Upload
st.markdown(
    "<h3 style='text-align: center; color:black;'>Upload as CSV or Enter Data Here</h3>",
    unsafe_allow_html=True,
)

uploaded_file = st.file_uploader("", label_visibility="collapsed", type="csv")
if uploaded_file is not None:
    st.session_state["data_to_share"] = pd.read_csv(uploaded_file)
    df_to_share = st.session_state["data_to_share"]


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

res = secret_share_component(
    data_dict, names, replication_factor, "secret_data_share_test"
)

# Event-driven call to handle submission
if st.button("Secret Share Data"):
    share_data_helper.handle_submission(engine, names, dtypes, replication_factor)

st.write(res)
