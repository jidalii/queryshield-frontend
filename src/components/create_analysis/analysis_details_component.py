import streamlit as st

from streamlit_extras.stylable_container import stylable_container
from models.analysis import *
from db.schema_validation import *
from db.db_services import *
from utils.row_detection import *
from configs.html import VALIDATION_CSS


def analysis_details_component() -> None:
    create_analysis_input = st.session_state["create_analysis_input"]
    if st.session_state.isvalid_analysis_details == "init":
        css_style = "init"
    else:
        css_style = st.session_state.isvalid_analysis_details == 1
    with stylable_container(
        key="analysis_details_model",
        css_styles=VALIDATION_CSS[css_style],
    ):
        create_analysis_input["query_name"] = st.text_input(
            "Query Name", create_analysis_input["query_name"]
        )
        create_analysis_input["query"] = st.text_area(
            "Input Query Here", create_analysis_input["query"]
        )
        create_analysis_input["description"] = st.text_area(
            "Description", create_analysis_input["description"]
        )

    if st.session_state.isvalid_analysis_details == 2:
        st.error("Error: No fields should be empty.")
    elif st.session_state.isvalid_analysis_details == 3:
        st.error("Error: Invalid SQL query.")
