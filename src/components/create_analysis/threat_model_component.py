import random

import streamlit as st

from streamlit_extras.stylable_container import stylable_container
from models.analysis import *
from db.schema_validation import *
from db.db_services import *
from utils.row_detection import *
from configs.configs import CLOUD_PROVIDERS, THREAT_MODELS, TYPE_MAPPING
from configs.html import VALIDATION_CSS


def threat_model_component() -> None:
    create_analysis_input = st.session_state["create_analysis_input"]
    css_style = (
        "init"
        if st.session_state.isvalid_threat_model == "init"
        else st.session_state.isvalid_threat_model == 1
    )
    with stylable_container(
        key="thread_model",
        css_styles=VALIDATION_CSS[css_style],
    ):
        col1, col2 = st.columns(2)
        new_threat_model = col1.radio(
            "Threat Model",
            options=THREAT_MODELS,
            label_visibility="collapsed",
            key="t1",
        )

        # Detect if the threat model has been changed
        if new_threat_model != create_analysis_input.get("threat_model", ""):
            create_analysis_input["threat_model"] = new_threat_model
            st.session_state.threat_model_changed = True
        else:
            st.session_state.threat_model_changed = False

        col2.markdown("##### Cloud Providers")

        if st.session_state.threat_model_changed:
            if create_analysis_input["threat_model"] == "Semi-Honest":
                create_analysis_input["selected_providers"] = random.sample(
                    CLOUD_PROVIDERS, 3
                )

            elif create_analysis_input["threat_model"] == "Malicious":
                create_analysis_input["selected_providers"] = random.sample(
                    CLOUD_PROVIDERS, 4
                )

        selected_providers: list[str] = create_analysis_input["selected_providers"]
        for provider in CLOUD_PROVIDERS:
            is_selected = col2.toggle(
                provider,
                key=f"toggle_{provider}",
                value=provider in selected_providers,
            )

            # Update selected_providers based on toggle state
            if is_selected and provider not in selected_providers:
                selected_providers.append(provider)
            elif not is_selected and provider in selected_providers:
                selected_providers.remove(provider)

    if st.session_state.isvalid_threat_model == 2:
        st.error(
            "Error: In the Semi-Honest threat model, you must select at least 3 cloud providers."
        )
    elif st.session_state.isvalid_threat_model == 3:
        st.error(
            "Error: In the Malicious threat model, you must select at least 4 cloud providers."
        )
