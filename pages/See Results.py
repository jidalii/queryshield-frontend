import streamlit as st 
import pandas as pd
st.set_page_config("QueryShield")

if "query_name" in st.session_state:
        st.title(f'{st.session_state.query_name} Results')

st.subheader("Analysis Results")
if "user_input" in st.session_state:
    if "column name" in st.session_state:
        column_name= st.session_state.user_input["Column Name"]
        if not column_name.empty:
            first_entry= column_name.iloc[0]
            df= pd.DataFrame(columns= [first_entry])
            st.dataframe(df, hide_index=True)
        else: st.write("The Data Schema is not defined.")



st.subheader("Data Schema")
if "user_input" in st.session_state:
    col1, col2, col3= st.columns(3)
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
    #st.write(f'Query Name: {st.session_state.query_name}')
    st.text_input("Query Name" , st.session_state.query_name)
if 'query' in st.session_state:
    #st.write(f'Query Entered: {st.session_state.query}')
    st.text_area('Query Entered', st.session_state.query )
if 'description' in st.session_state:
    #st.write(f'Description: {st.session_state.description}')
    st.text_area("Description", st.session_state.description)
