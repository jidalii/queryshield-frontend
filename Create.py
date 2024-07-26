import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from st_aggrid import AgGrid, GridOptionsBuilder
import time

st.set_page_config('QueryShield')

st.sidebar.title("QueryShield")
login= st.sidebar.button("Login")
@st.experimental_dialog("Login")
def email_form():
    with st.form('Login', border=False, clear_on_submit=True):
        name= st.text_input('Name', key= "key1")
        email= st.text_input('Email', key= "key2")
        if st.form_submit_button("Submit"):
            st.rerun()

if login:
    email_form()
    
st.title('Create New Analysis')
st.subheader('Data Schema')

with st.form("Submit", border=False, clear_on_submit=False):
    col1, col2, col3= st.columns(3)
    df= pd.DataFrame(columns=["Column Name",'Units (e.g.lbs, kg, MM/dd/yyyy)','Type'])
    numbers=["Integer", "Varchar", "String", "Catgeory"]
    st.session_state.user_input= st.data_editor(df, column_config= {"Type": st.column_config.SelectboxColumn("Type", options= ["Integer", "Varchar", "String", "Catgeory"], default="Integer"),
                                                                    "Column Name": st.column_config.TextColumn(),
                                                                    "Units (e.g.lbs, kg, MM/dd/yyyy)": st.column_config.TextColumn()}, 
                                                                    
                                                                     num_rows="dynamic", hide_index=True, use_container_width=True)
    
   

    column_name= st.session_state.user_input["Column Name"]
    if "column name" not in st.session_state:
        st.session_state["column name"]=""

    if 'user input' not in st.session_state:
        st.session_state["user input"]=""
   
    st.divider()
    st.subheader('Threat Model')

    col1, col2 =st.columns(2)
    st.session_state.threat_model= col1.radio("Threat Model", options=["Semi-Honest", "Malicious"],label_visibility= "collapsed")
    st.session_state.cloud_provider = col2.multiselect("Cloud Provider", options= ["AWS", "Microsoft Azure", "Google Cloud", "Chameleon Open Cloud"])
   
    if st.session_state.threat_model== "Semi-Honest":
        if len(st.session_state.cloud_provider)>=3:
            st.success("This is a success")
        elif len(st.session_state.cloud_provider) <3:
            st.error("You must select at least 3 cloud providers")

            
    if st.session_state.threat_model=="Malicious":
        if len(st.session_state.cloud_provider)>=4:
            st.success("This is a success")
        elif len(st.session_state.cloud_provider) <4:
            st.error("You must select all 4 cloud providers")
    if "threat_model" not in st.session_state:
        st.session_state['threat model']=""
    if "cloud provider" not in st.session_state:
        st.session_state["cloud provider"]=""
    st.divider()


    st.subheader('Analysis Details')

    st.session_state.query_name= st.text_input("Query Name")
    if 'query_name' not in st.session_state:
        st.session_state["query_name"]= ""

    st.session_state.query= st.text_area("Input Query Here")
    if "query" not in st.session_state:
        st.session_state['query']= ""
    st.session_state.description = st.text_area("Description")
    if "description" not in st.session_state:
        st.session_state['description']= ""
    st.divider()


    st.subheader("Complete Registration")
    submitted= st.form_submit_button("Submit")
    if submitted:
        st.session_state['query_name'] = st.session_state.query_name
        st.session_state['description'] = st.session_state.description
        st.session_state['query']= st.session_state.query
        st.session_state['threat model']= st.session_state.threat_model
        st.session_state['cloud provider']= st.session_state.cloud_provider
        st.session_state["user input"]= st.session_state.user_input
        st.write("Registration Completed")
  
        
