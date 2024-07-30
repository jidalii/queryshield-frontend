import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from st_aggrid import AgGrid, GridOptionsBuilder
import random
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


if "disabled" not in st.session_state:
            st.session_state["disabled"]= False
def disable():
            st.session_state["disabled"] =True

st.title('Create New Analysis')


st.subheader('Data Schema')




#with st.form("Submit", border=False, clear_on_submit=False):
col1, col2= st.columns([0.7, 0.3])
df= pd.DataFrame(columns=["Column Name",'Units (e.g.lbs, kg, MM/dd/yyyy)','Type'])
numbers=["Integer", "Varchar", "String", "Catgeory"]
st.session_state.user_input= col1.data_editor(df, column_config= {"Type": st.column_config.SelectboxColumn("Type", 
    options= ["Integer", "Varchar", "String", "Category"], default="Integer"),
                                                                        "Column Name": st.column_config.TextColumn(),
                                                                        "Units (e.g.lbs, kg, MM/dd/yyyy)": st.column_config.TextColumn()}, 
                                                                        
                                                                        num_rows="dynamic", hide_index=True, use_container_width=True)


if any(st.session_state.user_input["Type"] == "Category"):
    column_name= st.session_state.user_input["Column Name"]
    with col2.expander("Category"):
        if "num_rows" not in st.session_state:
            st.session_state.num_rows=1
        def add_row(): 
            st.session_state.num_rows+=1
        for i in range(st.session_state.num_rows):
            col2.text_input("", label_visibility="collapsed", key=f"Category Input Box_{i}")
        col2.button('Add New Category', on_click=add_row )   

        #df= pd.DataFrame(columns=[st.session_state.user_input["Column Name"]])
        #st.data_editor(df, num_rows="dynamic", use_container_width=True )

    #col1, col2= st.columns(2)
    #col1.text_input(f'Enter Category Name for {st.session_state.user_input['Column Name']}')
    #@st.experimental_dialog(f'Enter Categories')
    #def specify():
                #if st.session_state.user_input['Column Name'] not in st.session_state:
                    #st.session_state.user_input['Column Name']=''
                #df=pd.DataFrame(columns=[st.session_state.user_input["Column Name"]])
                #st.data_editor(df, num_rows="dynamic", use_container_width=True )
                #confirm= st.button("Confirm", help=None)
                #if confirm:
                    #st.button('Test')
    #specify()


   


column_name= st.session_state.user_input["Column Name"]
if "column name" not in st.session_state:
    st.session_state["column name"]=""

if 'user input' not in st.session_state:
    st.session_state["user input"]=""
    
st.divider()
st.subheader('Threat Model')

if "cloud provider" not in st.session_state:
    st.session_state["cloud provider"]=""


col1, col2 =st.columns(2)
st.session_state.threat_model= col1.radio("Threat Model", options=["Semi-Honest", "Malicious"],label_visibility= "collapsed")
    #st.session_state.cloud_provider = col2.multiselect("Cloud Provider", options= ["AWS", "Microsoft Azure", "Google Cloud", "Chameleon Open Cloud"])
    #st.session_state.cloud_provider= col2.toggle("Cloud Provider",)
col2.markdown("Cloud Provider")
st.session_state.cloud_provider={col2.toggle("AWS", key="toggle1"),col2.toggle("Microsoft Azure", key="toggle2"),
                col2.toggle("Google Cloud", key= "toggle3"), col2.toggle("Chameleon Open Cloud", key="toggle4")}



#if st.session_state.threat_model=='Malicious':
   
    
    #if len(st.session_state.cloud_provider)>3

        #random_toggle= random.sample(st.session_state.cloud_provider, 3)
    #if st.session_state.threat_model== "Malicious":
        
    
if "threat_model" not in st.session_state:
    st.session_state['threat model']=""
#if "cloud provider" not in st.session_state:
    #st.session_state["cloud provider"]=""
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


#st.text_input("Testing", disabled=st.session_state.disabled, on_change= disable)

st.subheader("Complete Registration")
#submitted= st.button("Submit")
#if submitted:
if st.button('Submit'):
        disable()  
        st.session_state['query_name'] = st.session_state.query_name
        st.session_state['description'] = st.session_state.description
        st.session_state['query']= st.session_state.query
        st.session_state['threat model']= st.session_state.threat_model
        st.session_state['cloud provider']= st.session_state.cloud_provider
        st.session_state["user input"]= st.session_state.user_input
        if st.session_state.threat_model== "Semi-Honest":
            if len(st.session_state.cloud_provider)>=3:
                st.success("Success")
            elif len(st.session_state.cloud_provider) <3:
                st.error("Error")

                
        if st.session_state.threat_model=="Malicious":
            if len(st.session_state.cloud_provider)>=4:
                st.success("Success")
            elif len(st.session_state.cloud_provider) <4:
                st.error("Error")
    
