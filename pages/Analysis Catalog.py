import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from st_aggrid import AgGrid, GridOptionsBuilder
from io import StringIO

st.set_page_config('QueryShield')

st.title("Analysis Catalog")
login= st.sidebar.button("Login")
@st.experimental_dialog("Login")
def email_form():
    with st.form('Login', border=True, clear_on_submit=True):
        name=st.text_input('Name',key= "key1")
        email=st.text_input('Email', key= "key2")
        st.form_submit_button("Submit")
if login:
    email_form()
#if 'query_name' in st.session_state:
    #if 'description'in st.session_state:
        #data = {'Analysis Name': [st.session_state['query_name']], 'Description':[st.session_state["description"]], "Owners Registered":"", "More Details":"", "Action":""}
        #df = pd.DataFrame(data)
        #grid_builder = GridOptionsBuilder.from_dataframe(df)
        #grid_builder.configure_selection(selection_mode="multiple", use_checkbox=False,header_checkbox=False)
        #grid_builder.configure_side_bar(filters_panel=True, columns_panel=True)
        #grid_builder.configure_default_column(filterable= True, editable= False)
        #grid_builder.configure_column('More Details', cellEditor='agSelectCellEditor')
        #grid_options = grid_builder.build()
        #AgGrid(df, fit_columns_on_grid_load=True, gridOptions=grid_options, height=200)
#else:
    #st.error("No input found. Please go to Create Analysis and enter some text.")



if "query_name" in st.session_state:
    if "description" in st.session_state:
        col1, col2, col3, col4, col5= st.columns((1, 1, 1.5, 1, 1))
        with col1.markdown("**Analysis Name**"):

            col1.write(st.session_state.query_name)
        with col2.markdown("**Description**"):
            col2.write(st.session_state.description)
        with col3.markdown("**Owners Registered**"):
            col3.write("6")
        col4.markdown("**More Details**")
        with col4.popover("ⓘ"):
            st.subheader("Data Schema")
            if "user_input" in st.session_state:
                data= st.session_state.user_input 
                df= pd.DataFrame(data)
                st.dataframe(df, hide_index=True, use_container_width=True)
            st.subheader("Threat Model")
            if "threat_model" in st.session_state:
                st.radio("Threat Model:", options=[st.session_state.threat_model])
            if "cloud provider" in st.session_state:
                st.selectbox("Cloud Provider:", options=[st.session_state.cloud_provider])
            st.subheader('Analysis Details')
            if "query_name" in st.session_state:
                st.write(f"Query Name: {st.session_state.query_name}")
            if 'query' in st.session_state:
                st.write("Query Entered:")
                st.code(st.session_state.query)
            if 'description' in st.session_state:
                st.write(f"Description: {st.session_state.description}")
        col5.markdown("**Action**")
        col5.page_link("pages/Share Data.py")

if "df" not in st.session_state:
    st.session_state.df= pd.DataFrame(columns=["Analysis Name", "Description", "Owners Registered", "More Details", "Action"])
if 'query_name' in st.session_state:
    if 'description' in st.session_state:
        data = {'Analysis Name': [st.session_state['query_name']], 'Description':[st.session_state['description']], 
                "Owners Registered":"", 'More Details':"ⓘ", "Action":"https://effective-cod-pjgwpv5r6r5r3qjp-8501.app.github.dev/Share_Data"}
        
        user_input_df= pd.DataFrame(data)
        st.session_state.df= pd.concat([st.session_state.df,user_input_df], ignore_index=True)
        df = pd.DataFrame(data)
        st.dataframe(st.session_state.df,
        column_config={"Query Name":st.column_config.TextColumn(), 
                        "Description": st.column_config.TextColumn(), 
                        "More Details": st.column_config.LinkColumn('More Details'), 
                        "Action": st.column_config.LinkColumn('Action', display_text="Share Data")}, hide_index=False, use_container_width=True)
    
    
        
    


else:
    st.error("No input found. Please go to Create Analysis and enter some text.")


                        
                        
#if "column_name" not in st.session_state:
    

#df= pd.DataFrame(columns=['Status','Name','Owners Registered','More Details', 'Action'])
#st.data_editor(df, column_config={
    #"Status": st.column_config.TextColumn(),
    #"Name":st.column_config.LinkColumn(),
    #"Owners Registered": st.column_config.NumberColumn(),
    #"More Details":st.column_config.Column(),
    #"Action":st.column_config.TextColumn(),
    #}, num_rows="dynamic", hide_index=True, use_container_width=True)


#df= pd.DataFrame(columns=["a",'b','c'])
#st.data_editor(df)