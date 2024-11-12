import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import pytz
from streamlit.components.v1 import html

from components.schema_table_component import schema_table_component
from components.sidebar_component import sidebar_login_component
from configs.configs import schema_types
from configs.html import html_contents
from utils.row_detection import fake_click
from utils.helpers import convert_dict_to_df, convert_dict_to_category_dict, fetch_name_and_type_tuple
from utils.db.db_services import fetch_single_analysis, register_data_owner,is_registered_owner
from utils.share_data_validation import validate_share_data, validate_share_data_file 

st.title("Share Data")

st.sidebar.title("QueryShield")

# if "logined" not in st.session_state:
#     st.session_state["logined"] = False

st.subheader('Data Schema')

engine = create_engine(
    "postgresql+psycopg2://user1:12345678!@localhost:5432/queryshield"
)
# sidebar_login_component(engine)

if "view_category_df" not in st.session_state:
    st.session_state['view_category_df'] ={}

if "cell_position" not in st.session_state:
    st.session_state["cell_position"] = (0, 0)

analysis = fetch_single_analysis(engine, st.query_params["aid"])
boston_tz = pytz.timezone('America/New_York')
time_created = analysis['time_created'].astimezone(boston_tz).strftime('%Y:%m:%d %H:%M')

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
category_dict = convert_dict_to_category_dict(raw_schema)

schema_table_component(schema, schema_types, category_dict)
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

st.divider()
names, types = fetch_name_and_type_tuple(raw_schema)

to_share_df = pd.DataFrame(columns=names)

if "data_to_share" not in st.session_state:
    st.session_state["data_to_share"] = pd.DataFrame(columns=names)
    
# if "data_to_share_file" not in st.session_state:
#     st.session_state["data_to_share_file"] = pd.DataFrame(columns=names)
    
column_config = {}
for i, (name, type_) in enumerate(zip(names, types)):
    if type_ == 'Category':
        column_config[name] = st.column_config.SelectboxColumn(
                name,
                options=category_dict[i],
                default=category_dict[i][0],
            )
    else:
        column_config[name] = st.column_config.TextColumn(name)
        
st.markdown("<h3 style='text-align: center; color:black;'>Upload as CSV </h3>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("", label_visibility="collapsed", type='csv')
if uploaded_file is not None:
    st.session_state['data_to_share'] = pd.read_csv(uploaded_file)
    to_share_df = st.session_state['data_to_share']
    
st.markdown("<h3 style='text-align: center; color: black;'>or Enter Data Here </h3>", unsafe_allow_html=True)
st.session_state["data_to_share"] = st.data_editor(
    to_share_df,
    num_rows="dynamic",
    hide_index=True,
    use_container_width=True,
)

st.session_state["data_to_share"]

submitted= st.button("Secret Share Data")
if submitted:
    # is_valid, err = validate_share_data(st.session_state["data_to_share"], types)
    is_valid, err = validate_share_data_file(st.session_state['data_to_share'], names, types)
    if is_valid:
        aid = st.query_params["aid"]
        uid = st.query_params["uid"]
        is_registered = is_registered_owner(engine, aid, uid)
        if is_registered:
            err = f"You've already registered for analysis id {aid}"
            st.error(err)
        else:
            succss, err = register_data_owner(engine, aid, uid)
            if succss:
                st.success("Success")
            else:
                res = f"Error: {err}"
                st.error(res)
    else:
        res = f"Error: {err}"
        st.error(res)
