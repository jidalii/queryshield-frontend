import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode, GridUpdateMode

st.set_page_config("QueryShield", layout="wide")

st.title("Analysis History")
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


def hello(row):
    st.write(f"Hello from row {row}")


# def history_table():
sample_data = {
    "Analysis ID": ["1012323", "103431346", "1134134173"],
    "Analysis Name": ["Query1", "Query2", "Query3"],
    "Analyst Name": ["Alice", "Alice", "Alice"],
    "Analyst ID": ["101", "101", "101"],
    "Time Created": ["2024-10-12 08:30", "2024-10-12 09:00", "2024-10-12 10:30"],
    "Analysis Description": [
        {"parameter_1": "value_1", "parameter_2": 100},
        {"parameter_1": "value_2", "parameter_2": 200},
        {"parameter_1": "value_3", "parameter_2": 300},
    ],
    "Owners Registered": [10, 20, 30],
    "Status": ["Created", "Ready", "Failed"],
}

projectlist = [["project1", "project2"], [1,2]]

test_df = pd.DataFrame(sample_data)
# test_df = pd.DataFrame(projectlist, columns=["Projects", 'num'])

# Build Grid Options for Ag-Grid
gd = GridOptionsBuilder.from_dataframe(test_df)
# gd.configure_pagination(enabled=True)
gd.configure_selection(selection_mode="single")

# Configure Action column with a URL renderer
gd.configure_column(
    "Status",
    headerName="Status",
    cellRenderer=JsCode(
        """
        class UrlCellRenderer {
        init(params) {
            this.eGui = document.createElement('a');
            this.eGui.innerText = params.data["Status"];
            this.eGui.setAttribute('href', '/Analysis_History?aid=' + params.data["Analysis ID"]);
            this.eGui.setAttribute('style', "text-decoration:none");
            this.eGui.setAttribute('target', "_blank");
        }
        getGui() {
            return this.eGui;
        }
        }
        """
    ),
)
gd.configure_column(
    "Analysis Description",
    headerName="Analysis Description",
    cellRenderer=JsCode(
        """
        class UrlCellRenderer {
        init(params) {
            this.eGui = document.createElement('a');
            this.eGui.innerText = "View Details";
            this.eGui.setAttribute('href', '/Analysis_Detail_View?aid=' + params.data["Analysis ID"]);
            this.eGui.setAttribute('style', "text-decoration:none");
            this.eGui.setAttribute('target', "_blank");
        }
        getGui() {
            return this.eGui;
        }
        }
        """
    ),
)

gridoptions = gd.build()

# Display the DataFrame in AgGrid within col1
grid_table = AgGrid(
    test_df,
    gridOptions=gridoptions,
    allow_unsafe_jscode=True,
    height=500,
    theme="streamlit",
    update_mode=GridUpdateMode.SELECTION_CHANGED,
)
