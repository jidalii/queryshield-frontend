import streamlit as st
import numpy as np
import pandas as pd
from io import StringIO
import time
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

if "user_input" in st.session_state:
    data= st.session_state.user_input 
    df= pd.DataFrame(data)
    st.dataframe(df, hide_index=True, use_container_width=True)
st.subheader("Threat Model")
col1, col2= st.columns(2)
if "threat_model" in st.session_state:
    col1.radio("Threat Model:", options=[st.session_state.threat_model], label_visibility="collapsed", 
               disabled= st.session_state.disabled, on_change="disabled")
if "AWS" in st.session_state:
    col2.toggle("AWS", value=st.session_state.AWS, disabled= st.session_state.disabled, on_change="disabled")
if "Microsoft" in st.session_state:
    col2.toggle("Microsoft", value=st.session_state.Microsoft, disabled= st.session_state.disabled, on_change="disabled")
if 'Google Cloud' in st.session_state:
    col2.toggle("Google Cloud", value=st.session_state.Google, disabled= st.session_state.disabled, on_change="disabled")
if 'Chameleon' in st.session_state:
    col2.toggle("Chameleon", value=st.session_state.Chameleon, disabled= st.session_state.disabled, on_change="disabled")

st.subheader('Analysis Details')
if "query_name" in st.session_state:
    st.write(f"Query Name:{st.session_state.query_name}")
    #st.write(st.session_state.query_name)
    #st.text_input("Query Name" , st.session_state.query_name)
if 'query' in st.session_state:
    st.write("Query Entered:")
    st.code(st.session_state.query)
    #st.text_area('Query Entered', st.session_state.query )
if 'description' in st.session_state:
    st.write(f'Description:{st.session_state.description}')
    #st.write(st.session_state.description)
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


if "user_input" in st.session_state:
    if "column name" and "category schema" in st.session_state:
        column_name= st.session_state.user_input["Column Name"]
        entries= []
        for i in range(len(column_name)):
            entry= column_name[i]
            if entry:
                entries.append(entry)
        df= pd.DataFrame(columns= [entries])
        #def options():
            #if any(st.session_state.user_input["Type"])=='Category':
                #st.column_config.SelectboxColumn(label= [st.session_state.user_input["Category Name"]], options= [st.session_state.category_schema])
        st.data_editor(df, hide_index=True, num_rows="dynamic", use_container_width=False, 
                       column_config={st.column_config.SelectboxColumn(options= [st.session_state.category_schema])})

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


submitted= st.button("Secret Share Data")
if submitted:
    st.success("Success")