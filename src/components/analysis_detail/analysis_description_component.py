import streamlit as st


def view_threat_model_component(data):
    st.subheader("Threat Model")
    thread_model = data["threat_model"]
    st.markdown(f"- {thread_model}")
    st.markdown("#### Cloud Provider:")
    cloud_providers = data['selected_providers']
    for provider in cloud_providers:
        st.markdown("- " + provider)
    
        
def view_analysis_details_component(data):
    st.subheader("Analysis Details")
    if "query_name" in data:
        st.markdown("#### Query Name:")
        query_name = data["query_name"]
        st.write(f"{query_name}")
    if "query" in data:
        st.markdown("#### Query:")
        st.code(data["query"], language='sql')
    if "description" in data:
        st.markdown("#### Description:")
        description = data["description"]
        st.write(f"{description}")