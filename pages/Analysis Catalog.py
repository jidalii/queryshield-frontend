import streamlit as st
import pandas as pd
import numpy as np
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode

st.set_page_config("QueryShield", layout="wide")

st.title("Analysis Catalog")
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

st.session_state.user_input_changed

if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame(
        columns=[
            "Analysis Name",
            "Description",
            "Owners Registered",
            "More Details",
            "Action",
        ]
    )


if "query_name" in st.session_state:
    if "description" in st.session_state:
        data = {
            "Analysis Name": [st.session_state["query_name"]],
            "Description": [st.session_state["description"]],
            "Owners Registered": "",
            "More Details": "ⓘ",
            "Action": "https://effective-cod-pjgwpv5r6r5r3qjp-8501.app.github.dev/Share_Data",
        }

# empty_df = pd.DataFrame(
#     {
#         "analyst_name": pd.Series(dtype="str"),
#         "analyst_id": pd.Series(dtype="int"),
#         "analysis_specification": pd.Series(
#             dtype="object"
#         ),  # Could be JSON data in string form
#         "number_of_owners_registered": pd.Series(dtype="int"),
#         "option_to_share_data": pd.Series(
#             dtype="str"
#         ),  # Data sharing status (create, start, running, completed, failed)
#         "timestamp": pd.Series(dtype="object"),  # Timestamp as a string
#     }
# )


def catalog_container(request_data):
    col1, col2, col3, col4, col5, col6 = st.columns((1, 1, 1, 3, 1, 1))
    col1.markdown("**Analysis Name**")
    col2.markdown("**Analysis ID**")
    col3.markdown("**Time Created**")
    col4.markdown("**Analysis Description**")
    col5.markdown("**Owners Registered**")
    col6.markdown("**Action**")
    for i, request in enumerate(request_data):
        col1.write(request[0])
        col2.write(str(request[1]))
        col3.write(request[2])
        with col4.popover("ⓘ", use_container_width=True):
            st.subheader("Data Schema")
        col5.write(str(request[4]))
        url = f"http://localhost:8501/Share_Data/?request_id={request[0]}"
        col6.link_button(label="Share Data", url=url)
    with col4.popover("ⓘ", use_container_width=True):
        st.subheader("Data Schema")
        if "user_input" in st.session_state:
            data = st.session_state.user_input
            df = pd.DataFrame(data)
            st.dataframe(df, hide_index=True, use_container_width=True)
        st.subheader("Threat Model")
        if "threat_model" in st.session_state:
            st.radio(
                "Threat Model:",
                options=[st.session_state.threat_model],
                disabled=st.session_state.disabled,
                on_change="disabled",
            )
        st.write("Cloud Providers")
        if "AWS" in st.session_state:
            st.toggle(
                "AWS",
                value=st.session_state.AWS,
                disabled=st.session_state.disabled,
                on_change="disabled",
            )
        if "Microsoft" in st.session_state:
            st.toggle(
                "Microsoft",
                value=st.session_state.Microsoft,
                disabled=st.session_state.disabled,
                on_change="disabled",
            )
        if "Google Cloud" in st.session_state:
            st.toggle(
                "Google Cloud",
                value=st.session_state.Google,
                disabled=st.session_state.disabled,
                on_change="disabled",
            )
        if "Chameleon" in st.session_state:
            st.toggle(
                "Chameleon",
                value=st.session_state.Chameleon,
                disabled=st.session_state.disabled,
                on_change="disabled",
            )
        # if "cloud provider" in st.session_state:
        # st.selectbox("Cloud Provider:", options=[st.session_state.cloud_provider])
        st.subheader("Analysis Details")
        if "query_name" in st.session_state:
            st.write(f"Query Name: {st.session_state.query_name}")
        if "query" in st.session_state:
            st.write("Query Entered:")
            st.code(st.session_state.query)
        if "description" in st.session_state:
            st.write(f"Description: {st.session_state.description}")


sample_data = [
    (
        "Alice",
        101,
        "2024-10-12 08:30",
        {"parameter_1": "value_1", "parameter_2": 100},
        10,
        "http://localhost:8501/Share_Data",
    ),
    (
        "Bob",
        106,
        "2024-10-12 09:00",
        {"parameter_1": "value_2", "parameter_2": 200},
        20,
        "http://localhost:8501/Share_Data",
    ),
    (
        "Charlie",
        103,
        "2024-10-12 09:30",
        {"parameter_1": "value_3", "parameter_2": 300},
        30,
        "http://localhost:8501/Share_Data",
    ),
]


sample_data = {
    "Analysis ID": ["123456", "123457", "123458"],
    "Analysis Name": ["Analysis A", "Analysis B", "Analysis C"],
    "Analyst Name": ["Alice", "Bob", "Charlie"],
    "Analyst ID": [101, 106, 173],
    "Time Created": ["2024-10-12 08:30", "2024-10-12 09:00", "2024-10-12 09:30"],
    "Analysis Description": [
        {"parameter_1": "value_1", "parameter_2": 100},
        {"parameter_1": "value_2", "parameter_2": 200},
        {"parameter_1": "value_3", "parameter_2": 300},
    ],
    "Owners Registered": [10, 20, 30],
}

# Convert the dictionary into a Pandas DataFrame
test_df = pd.DataFrame(sample_data)

# Create grid options for Ag-Grid
gd = GridOptionsBuilder.from_dataframe(test_df)

# Example for configuring a column with a custom cell renderer
gd.configure_column(
    "Analysis Description",
    headerName="Analysis Description",
    cellRenderer=JsCode(
        """
        class UrlCellRenderer {
          init(params) {
            this.eGui = document.createElement('a');
            this.eGui.innerText = "See Details";
            this.eGui.setAttribute('href', '/Analysis_Detail_View?request_id=' + params.data["Analysis Name"]);
            console.log(params);
            this.eGui.setAttribute('style', "text-decoration:none");
            this.eGui.setAttribute('target', "_blank");
          }
          getGui() {
            return this.eGui;
          }
        }
        """
    ),
    width=300,
)

gd.configure_column(
    "Action",
    headerName="Action",
    cellRenderer=JsCode(
        """
        class UrlCellRenderer {
          init(params) {
            this.eGui = document.createElement('a');
            this.eGui.innerText = "Share Data";
            this.eGui.setAttribute('href', '/Share_Data?request_id=' + params.data["Analysis Name"]);
            console.log(params);
            this.eGui.setAttribute('style', "text-decoration:none");
            this.eGui.setAttribute('target', "_blank");
          }
          getGui() {
            return this.eGui;
          }
        }
        """
    ),
    width=300,
)

# Build the grid options
gridoptions = gd.build()

# Display the DataFrame in AgGrid
AgGrid(
    test_df,
    gridOptions=gridoptions,
    allow_unsafe_jscode=True,
    height=500,
    # theme="alpine",
)
