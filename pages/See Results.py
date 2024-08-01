import streamlit as st 
import pandas as pd
st.set_page_config("QueryShield")

if "query_name" in st.session_state:
        st.title(f'{st.session_state.query_name} Results')

st.subheader("Analysis Results")
if "Submit" in st.session_state:
    if "user_input" in st.session_state:
        if "column name" in st.session_state:
            column_name= st.session_state.user_input["Column Name"]
            if not column_name.empty:
                first_entry= column_name.iloc[0]
                df= pd.DataFrame(columns= [first_entry])
                st.dataframe(df, hide_index=True, width=200)
else:st.write("The Data Schema is not defined.")




if "Submit" and "disabled" in st.session_state:
    if "user_input" in st.session_state:
        st.subheader("Data Schema")
        col1, col2, col3= st.columns(3)
        data= st.session_state.user_input 
        df= pd.DataFrame(data)
        st.dataframe(df, hide_index=True, use_container_width=True)
    st.subheader("Threat Model")
    col1,col2=st.columns(2)
    if "threat_model" in st.session_state:
        col1.radio("Threat Model:", options=[st.session_state.threat_model], label_visibility="collapsed", disabled=st.session_state.disabled, on_change="disabled")
    if "AWS" in st.session_state:
        col2.toggle("AWS", value=st.session_state.AWS, disabled=st.session_state.disabled, on_change="disabled")
    if "Microsoft" in st.session_state:
        col2.toggle("Microsoft", value=st.session_state.Microsoft, disabled=st.session_state.disabled, on_change="disabled")
    if 'Google Cloud' in st.session_state:
        col2.toggle("Google Cloud", value=st.session_state.Google, disabled=st.session_state.disabled, on_change="disabled")
    if 'Chameleon' in st.session_state:
        col2.toggle("Chameleon", value=st.session_state.Chameleon, disabled=st.session_state.disabled, on_change="disabled")
    st.subheader('Analysis Details')
    if "query_name" and "disabled" in st.session_state:
        st.write(f'Query Name: {st.session_state.query_name}')
    if 'query' in st.session_state:
        st.write("Query Entered:")
        st.code(st.session_state.query)
    if 'description' in st.session_state:
        st.write(f'Description: {st.session_state.description}')
else: st.empty()