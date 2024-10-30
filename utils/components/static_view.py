import streamlit as st

def view_threat_model():
    st.subheader("Threat Model")
    create_analysis_input = st.session_state["create_analysis_input"]
    thread_model = create_analysis_input["threat_model"]
    st.markdown(f"- {thread_model}")
    st.markdown("#### Cloud Provider:")
    cloud_providers = ["Google Cloud", "Microsoft Azure", "Cloud 1"]
    for provider in cloud_providers:
        st.markdown("- " + provider)
    
        
def view_analysis_details():
    create_analysis_input = st.session_state["create_analysis_input"]
    st.subheader("Analysis Details")
    if "query_name" in create_analysis_input:
        st.markdown("#### Query Name:")
        query_name = create_analysis_input["query_name"]
        st.write(f"{query_name}")
    if "query" in create_analysis_input:
        st.markdown("#### Query:")
        st.code(create_analysis_input["query"], language='sql')
    if "description" in create_analysis_input:
        st.markdown("#### Description:")
        description = create_analysis_input["description"]
        st.write(f"{description}")