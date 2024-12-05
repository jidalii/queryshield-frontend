import streamlit as st
import pandas as pd


def initialize_session_state():
    if "table_name" not in st.session_state:
        st.session_state["table_name"] = ""
    if "cell_position" not in st.session_state:
        st.session_state["cell_position"] = (0, 0)

    if "create_analysis_input" not in st.session_state:
        st.session_state["create_analysis_input"] = {}

    create_analysis_input = st.session_state["create_analysis_input"]

    if "table_name" not in create_analysis_input:
        create_analysis_input["table_name"] = ""
    if "temp_enums" not in st.session_state:
        st.session_state["temp_enums"] = []


    if "user_input" not in create_analysis_input:
        create_analysis_input["user_input"] = pd.DataFrame()
    if "previous_df" not in st.session_state:
        st.session_state.previous_df = pd.DataFrame([])
    if "category_schema" not in create_analysis_input:
        create_analysis_input["category_schema"] = {}
    if "schema_types" not in st.session_state:
        st.session_state.schema_types = []
    if "user_input_changed" not in st.session_state:
        st.session_state.user_input_changed = 0
        
    if "threat_model" not in create_analysis_input:
        create_analysis_input["threat_model"] = ""
    if "selected_providers" not in create_analysis_input:
        create_analysis_input["selected_providers"] = []
    if "isvalid_threat_model" not in st.session_state:
        st.session_state["isvalid_threat_model"] = "init"
    if "isvalid_analysis_details" not in st.session_state:
        st.session_state["isvalid_analysis_details"] = "init"
    if "isvalid_sql" not in st.session_state:
        st.session_state["isvalid_sql"] = True
