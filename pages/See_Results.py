import streamlit as st
import pandas as pd


st.set_page_config("QueryShield")

st.sidebar.title("QueryShield")
login = st.sidebar.button("Login")

@st.experimental_dialog("Login")
def email_form():
    with st.form("Login", border=True, clear_on_submit=True):
        name = st.text_input("Name", key="key1")
        email = st.text_input("Email", key="key2")
        st.form_submit_button("Submit")


if login:
    email_form()

if "query_name" in st.session_state:
    st.title(f"{st.session_state.query_name} Results")

if "Sumbit" not in st.session_state:
    st.session_state["Submit"] = False

if "Submit" in st.session_state:
    if "user_input" in st.session_state:
        if "column name" in st.session_state:
            column_name = st.session_state.user_input["Column Name"]
            if not column_name.empty:
                first_entry = column_name.iloc[0]
                df = pd.DataFrame(columns=[first_entry])
                st.dataframe(df, hide_index=True, width=200)

if "Submit" and "disabled" in st.session_state:
    if "user_input" in st.session_state:
        st.subheader("Data Schema")
        col1, col2, col3 = st.columns(3)
        data = st.session_state.user_input
        df = pd.DataFrame(data)
        st.dataframe(df, hide_index=True, use_container_width=True)
    st.subheader("Threat Model")
    col1, col2 = st.columns(2)
    col2.markdown("#### Cloud Providers")
    if "threat_model" in st.session_state:
        col1.radio(
            "Threat Model:",
            options=[st.session_state.threat_model],
            label_visibility="collapsed",
            disabled=st.session_state.disabled,
            on_change="disabled",
        )
    if "selected_providers" in st.session_state:
        for _, provider in enumerate(st.session_state.selected_providers):
            col2.markdown(f"- {provider}")
    st.subheader("Analysis Details")
    if "query_name" and "disabled" in st.session_state:
        st.write(f"Query Name: {st.session_state.query_name}")
    if "query" in st.session_state:
        st.write("Query Entered:")
        st.code(st.session_state.query)
    if "description" in st.session_state:
        st.write(f"Description: {st.session_state.description}")
else:
    st.empty()
