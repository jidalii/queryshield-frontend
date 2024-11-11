import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import pytz

from components.schema_table_component import schema_table_component
from configs.configs import schema_types
from utils.components.static_view import view_threat_model, view_analysis_details
from utils.helpers import convert_dict_to_df, convert_dict_to_category_dict, fetch_name_and_type_tuple
from utils.db.db_services import fetch_single_analysis
from utils.share_data_validation import validate_share_data

st.set_page_config(
    page_title='QueryShield',
    layout="wide",
    initial_sidebar_state="expanded",)
st.title("Share Data")

st.sidebar.title("QueryShield")
login= st.sidebar.button("Login")
@st.experimental_dialog("Login")
def email_form():
    with st.form('Login', border=True, clear_on_submit=True):
        name=st.text_input('Name',key= "key1")
        email=st.text_input('Email', key= "key2")
        st.form_submit_button("Submit")
if login:
    email_form()

st.subheader('Data Schema')

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

st.divider()
names, types = fetch_name_and_type_tuple(raw_schema)

to_share_df = pd.DataFrame(columns=names)

if "data_to_share" not in st.session_state:
    st.session_state["data_to_share"] = pd.DataFrame(columns=names)
    
column_config = {}
for i, (name, type_) in enumerate(zip(names, types)):
    if type_ == 'Category':
        column_config[name] = st.column_config.SelectboxColumn(
                "Type",
                options=category_dict[i],
                default=category_dict[i][0],
            )
    else:
        column_config[name] = st.column_config.TextColumn(name)
        
st.markdown("<h3 style='text-align: center; color: black;'>Enter Data Here </h3>", unsafe_allow_html=True)
st.session_state["data_to_share"] = st.data_editor(
    to_share_df,
    column_config=column_config,
    num_rows="dynamic",
    hide_index=True,
    use_container_width=True,
)

st.session_state["data_to_share"]

st.markdown("<h3 style='text-align: center; color:black;'>or Upload as CSV </h3>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("", label_visibility="collapsed", type='csv')
if uploaded_file is not None:
    dataframe = pd.read_csv(uploaded_file)
    st.write(dataframe)
    

submitted= st.button("Secret Share Data")
if submitted:
    if validate_share_data(st.session_state["data_to_share"], types):
        st.success("Success")
    else:
        st.error("Error")