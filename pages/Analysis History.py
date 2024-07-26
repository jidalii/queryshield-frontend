import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from st_aggrid import AgGrid, GridOptionsBuilder
from st_aggrid import JsCode
st.set_page_config("QueryShield")

st.title("Analysis History")
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

if "query_name" in st.session_state:
     col1, col2,col3,col4= st.columns(4)
     col1.markdown("**Status**")
     col2.markdown("**Query Name**")
     col2.write(st.session_state.query_name)
     col3.markdown("**Owners Registered**")
     col4.markdown("**Action**")
     col4.page_link("pages/See Results.py")

#df= pd.DataFrame(columns=['Status','Name','Owners Registered', 'Action'])
#st.data_editor(df, column_config={ 
        #"Status": st.column_config.TextColumn(),
        #"Name":st.column_config.LinkColumn(),
        #"Owners Registered": st.column_config.NumberColumn(),
        #"Action":st.column_config.TextColumn(),
        #}, hide_index=True, num_rows="dynamic", use_container_width=True)


#search_query= st.text_input('Search here')
if 'query_name' in st.session_state:
        data= {"Status":"", 'Query Name': [st.session_state['query_name']], "Owners Registered":"", "Action":"pages/See Results.py"}
        df = pd.DataFrame(data)
        st.dataframe(df, column_config={"Query Name":st.column_config.LinkColumn(), 
                                        "Action": st.column_config.LinkColumn("Action", display_text="See Results")}, hide_index=True, use_container_width=True)
else:
    st.error("No input found. Please go to page 1 and enter some text.")




#if 'query_name' in st.session_state:
    #data = {"Status":"", 'Query Name': [st.session_state['query_name']], "Owners Registered":"", "Action":"See Results"}
    #df = pd.DataFrame(data)
    #grid_builder = GridOptionsBuilder.from_dataframe(df)
    #grid_builder.configure_selection(selection_mode="multiple", use_checkbox=True,header_checkbox=True)
    #grid_builder.configure_side_bar(filters_panel=True, columns_panel=True)
    #grid_builder.configure_default_column(filterable= True, editable= True, )
    #grid_builder.configure_column("Action", )
    #grid_options= grid_builder.build()
    #AgGrid(df, fit_columns_on_grid_load=True, gridOptions=grid_options, height=300)
#else:
    #st.error("No input found. Please go to page 1 and enter some text.")


#if 'query_name' in st.session_state:
    #columns= st.columns ((1, 2, 2, 2, 2))
    #fields = ["#", "Status", 'Analysis Name',"Owners Registered", 'Action']
    #for col, field_name in zip(columns, fields):
        #col.write(field_name)
    #for x, email in enumerate(""):
                #col1, col2, col3, col4, col5= st.columns((1, 2, 2, 2, 2))
                #col1.write("#")  
                #col2.write([st.session_state["query_name"]])  # email
                #col3.write([st.session_state["query_name"]])  # unique ID
                #col4.link_button("Success", "https://mail.google.com/mail/u/0/#inbox")   # email status
#else:
    #st.error("No input found. Please go to page 1 and enter some text.")



#st.data_editor(df, column_config={"key":"value"}, hide_index=1 , num_rows="dynamic")
#st.column_config.LinkColumn("status")