import streamlit as st
import numpy as np
import pandas as pd
from io import StringIO
import time
st.set_page_config('QueryShield')
st.title("Share Data")

st.subheader('Data Schema')
if "user_input" in st.session_state:
    data= st.session_state.user_input 
    df= pd.DataFrame(data)
    st.dataframe(df, hide_index=True, use_container_width=True)
st.subheader("Threat Model")
col1, col2= st.columns(2)
if "threat_model" in st.session_state:
    col1.radio("Threat Model:", options=[st.session_state.threat_model], label_visibility="collapsed")
if "cloud provider" in st.session_state:
    col2.multiselect("Cloud Provider:", options=[st.session_state.cloud_provider], placeholder="")
st.subheader('Analysis Details')
if "query_name" in st.session_state:
    st.write("Query Name:")
    st.write(st.session_state.query_name)
    #st.text_input("Query Name" , st.session_state.query_name)
if 'query' in st.session_state:
    st.write("Query Entered:")
    st.code(st.session_state.query)
    #st.text_area('Query Entered', st.session_state.query )
if 'description' in st.session_state:
    st.write('Description:')
    st.write(st.session_state.description)
    #st.text_area("Description", st.session_state.description)



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

with st.form("Secret Share Data", clear_on_submit=True, border=False):
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
            st.data_editor(df, hide_index=True, num_rows="dynamic", use_container_width=False)
        
    st.markdown("<h3 style='text-align: center; color:black;'>or Upload as CSV </h3>", unsafe_allow_html=True)

    #with st.form("Secret Share Data", border=False, clear_on_submit=True):
    uploaded_file = st.file_uploader("", label_visibility="collapsed")
    if uploaded_file is not None:
        # To read file as bytes:
        bytes_data = uploaded_file.getvalue()
        #st.write(bytes_data)

        # To convert to a string based IO:
        stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
        #st.write(stringio)

        # To read file as string:
        string_data = stringio.read()
        #st.write(string_data)

        # Can be used wherever a "file-like" object is accepted:
        dataframe = pd.read_csv(uploaded_file)
        st.write(dataframe)


        if len(dataframe.columns)> len(df.columns):
                st.error("File does not match schema")
        elif len(dataframe.columns)< len(df.columns):
            st.error("File does not match schema")


    submitted= st.form_submit_button("Secret Share Data")
    if submitted:
        #st.spinner(1)
        st.write("Sent")