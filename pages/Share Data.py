import streamlit as st
import numpy as np
import pandas as pd
from io import StringIO
import time
from utils.components.static_view import view_threat_model, view_analysis_details


st.set_page_config('QueryShield')
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




# if not st.query_params.request_id:
#     st.error("Request ID should be provided.")
# else:
#     st.session_state["request_id_share_data"] = st.query_params.request_id
#     print("request id: ", st.session_state["request_id_share_data"])

if "create_analysis_input" in st.session_state and "user_input" in st.session_state["create_analysis_input"]:
    data= st.session_state["create_analysis_input"]['user_input']
    df= pd.DataFrame(data)
    st.dataframe(df, hide_index=True, use_container_width=True)

view_threat_model()

view_analysis_details()


st.divider()

#if "user_input" in st.session_state:
   #if "column name" in st.session_state:
        #column_name= st.session_state.user_input["Column Name"]
        #entries= [column_name.to_string()]
        #if not column_name.empty:
            #df= pd.DataFrame(columns= [entries])
            #st.data_editor(df, num_rows="dynamic")
        #else: 
            #df= pd.DataFrame(columns= [""])
            #st.data_editor(df, num_rows="dynamic")

#with st.form("Secret Share Data", clear_on_submit=True, border=False):
st.markdown("<h3 style='text-align: center; color: black;'>Enter Data Here </h3>", unsafe_allow_html=True)
if "user_input" in st.session_state:
    if "column name" in st.session_state:
        column_name= st.session_state.user_input["Column Name"]
        entries= []
        for i in range(len(column_name)):
            entry= column_name[i]
            if entry:
                entries.append(entry)
        df= pd.DataFrame(columns= [entries])
        st.data_editor(df, hide_index=True, num_rows="dynamic", use_container_width=False,) 
if "create_analysis_input" in st.session_state and "user_input" in st.session_state["create_analysis_input"]:
    column_names = st.session_state["create_analysis_input"]['user_input']['name'].tolist()
    print(column_names)
    df= pd.DataFrame(columns= [column_names])
    st.data_editor(df, hide_index=True, num_rows="dynamic", use_container_width=False,) 


if "data_share_input" in st.session_state:
    if "column name" and "category schema" in st.session_state:
        column_name= st.session_state.data_share_input["Column Name"]
        entries= []
        for i in range(len(column_name)):
            entry= column_name[i]
            if entry:
                entries.append(entry)
        df= pd.DataFrame(columns= [entries])
        # st.data_editor(df, hide_index=True, num_rows="dynamic", use_container_width=False, 
        #                column_config={st.column_config.SelectboxColumn(options= [st.session_state.category_schema])})

st.markdown("<h3 style='text-align: center; color:black;'>or Upload as CSV </h3>", unsafe_allow_html=True)

#with st.form("Secret Share Data", border=False, clear_on_submit=True):
uploaded_file = st.file_uploader("", label_visibility="collapsed", type='csv')
if uploaded_file is not None:
    dataframe = pd.read_csv(uploaded_file)
    st.write(dataframe)

#     if len(dataframe.columns)> len(df.columns):
#         st.error("File does not match schema")
#     elif len(dataframe.columns)< len(df.columns):
#         st.error("File does not match schema")

# submitted= st.button("Secret Share Data")
# if submitted:
#     st.success("Success")