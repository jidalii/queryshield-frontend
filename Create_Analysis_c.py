from __future__ import annotations

import json
import os
import threading
import json
import asyncio
import random

from dataclasses import dataclass
from typing import Any

import pandas as pd
import numpy as np
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode, JsCode
import sqlalchemy

import streamlit as st
from streamlit import config
from streamlit import session_state as ss
from streamlit.components.v1 import html

import streamlit.web.bootstrap
from streamlit.web.server import Server
from streamlit.web.server.server import start_listening
from streamlit.web.server.media_file_handler import MediaFileHandler
from streamlit.web.server.server_util import make_url_path_regex

from streamlit_extras.stylable_container import stylable_container

from sqlalchemy import create_engine

from itertools import chain
from multiprocessing.shared_memory import SharedMemory

from tornado.web import RequestHandler


st.set_page_config(
    page_title="QueryShield",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.sidebar.title("QueryShield")
login = st.sidebar.button("Login")


@st.experimental_dialog("Login")
def email_form():
    with st.form("Login", border=False, clear_on_submit=True):
        name = st.text_input("Name", key="key1")
        email = st.text_input("Email", key="key2")
        if st.form_submit_button("Submit"):
            st.rerun()


if login:
    email_form()


if "disabled" not in st.session_state:
    st.session_state["disabled"] = False


def disable():
    st.session_state["disabled"] = True


def submit_btn():
    return st.button("Submit")


st.title("Create New Analysis")


# ******* click detection start
_JS_TO_PD_COL_OFFSET: int = -2

# Create shared memory for the payload
try:
    payload_memory = SharedMemory(name="JS_PAYLOAD", create=True, size=128)
except FileExistsError:
    payload_memory = SharedMemory(name="JS_PAYLOAD", create=False, size=128)


@dataclass
class Selection:
    """Dataclass to store the selected cell information."""

    col: int
    row: int
    sorted_by: int


def sort_df_by_selected_col(table: pd.DataFrame, js_sorted_by: int) -> pd.DataFrame:
    if js_sorted_by == 1:
        return table
    elif js_sorted_by == -1:
        return table.sort_index(axis=0, ascending=False)
    sorting_col: str = table.columns[abs(js_sorted_by) + _JS_TO_PD_COL_OFFSET]
    return table.sort_values(by=sorting_col, ascending=js_sorted_by > 0)


def _retrieve_payload() -> Selection:
    """Retrieve the payload from the shared memory and return it as a tuple."""
    payload = {}
    if payload_memory.buf[0] != 0:
        payload_bytes = bytearray(payload_memory.buf[:])
        payload_str = payload_bytes.decode("utf-8").rstrip("\x00")
        payload_length, payload = len(payload_str), json.loads(payload_str)
        payload_memory.buf[:payload_length] = bytearray(payload_length)
    if payload:
        selected_cell_info = Selection(
            *(
                int(val)
                for val in chain(
                    payload.get("cellId").split(","), [payload.get("sortedByCol")]
                )
            )
        )
        print(
            f"{os.getpid()}::{threading.get_ident()}: Streamlit callback received payload: {selected_cell_info}"
        )
        return Selection(
            selected_cell_info.col - 1,
            selected_cell_info.row,
            selected_cell_info.sorted_by,
        )
    else:
        print(
            f"{os.getpid()}::{threading.get_ident()}: Streamlit callback saw no payload!"
        )
        return Selection(-1, -1, -1)


def _interpret_payload(payload: Selection) -> tuple[Any, Any]:
    """Interpret the payload and return the selected row and column."""
    sorted_df = sort_df_by_selected_col(ss.user_input, payload.sorted_by)
    selected_row = sorted_df.index[payload.row]
    selected_col = sorted_df.columns[payload.col] if payload.col >= 0 else None

    # Update a text field:
    selection_str = (
        f", with contents: `{sorted_df.iat[payload.row, payload.col]}`"
        if selected_col
        else ""
    )
    ss["CELL_ID"] = (
        f"Clicked on cell with index [{selected_row}, {selected_col}]"
        f" (at position [{payload.row}, {payload.col}])"
        f"{selection_str}."
    )
    return selected_row, selected_col


def fake_click(*args, **kwargs):
    parsed_payload: Selection = _retrieve_payload()
    selected_row, selected_col = _interpret_payload(parsed_payload)
    ss["SELECTION"] = selected_row, selected_col


class JSCallbackHandler(RequestHandler):
    def set_default_headers(self):
        self.set_header(
            "Access-Control-Allow-Origin", "*"
        )  # Allow cross-origin requests if needed
        self.set_header("Access-Control-Allow-Methods", "POST")  # Allow POST method
        self.set_header(
            "Access-Control-Allow-Headers", "Content-Type"
        )  # Allow content type header

        try:
            payload: bytes = self.request.body
            print(
                f"{os.getpid()}::{threading.get_ident()}: Python received payload: {json.loads(payload)}"
            )
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON payload!")

        if payload_memory.buf[0] == 0:
            payload_memory.buf[: len(payload)] = payload
            print(
                f"{os.getpid()}::{threading.get_ident()}: Payload {payload} stored in shared memory"
            )


class CustomServer(Server):

    async def start(self):
        # Override the start of the Tornado server, so we can add custom handlers
        app = self._create_app()

        # Add a new handler
        app.default_router.add_rules(
            [
                (r"/js_callback", JSCallbackHandler),
            ]
        )

        # Our new rules go before the rule matching everything, reverse the list
        app.default_router.rules = list(reversed(app.default_router.rules))

        start_listening(app)
        await self._runtime.start()


# ******* clickc detection end


schema_types = ["Integer", "Varchar", "String", "Float", "Category"]

if "test" not in st.session_state:
    st.session_state.test = pd.DataFrame(
        {"Column Name": [""], "Units (e.g.lbs, kg, MM/dd/yyyy)": [""], "Type": [""]}
    )
    st.session_state.test = st.session_state.test.sort_index()


# def schema_container():
#     gb = GridOptionsBuilder.from_dataframe(st.session_state.test)

#     string_to_add_row = """
#         function(e) {
#             let api = e.api;
#             let rowIndex = e.rowIndex + 1;
#             api.applyTransaction({
#                 addIndex: rowIndex,
#                 add: [{"Column Name": "", "Units (e.g.lbs, kg, MM/dd/yyyy)": "", "Type": ""}]
#             });
#         }
#     """

#     string_to_delete = """
#         function(e) {
#             let api = e.api;
#             let sel = api.getSelectedRows();
#             let selectedRows = api.getSelectedRows();
#             if (selectedRows.length > 0) {
#                 api.applyTransaction({ remove: selectedRows });
#             } else {
#                 console.log('No rows selected for deletion.');
#             }
#         };
#     """

#     cell_button_add = JsCode(
#         """
#         class BtnAddCellRenderer {
#             init(params) {
#                 this.params = params;
#                 this.eGui = document.createElement('div');
#                 this.eGui.innerHTML = `
#                 <span>
#                     <style>
#                     .btn_add {
#                     background-color: limegreen;
#                     border: none;
#                     color: white;
#                     text-align: center;
#                     text-decoration: none;
#                     display: inline-block;
#                     font-size: 10px;
#                     font-weight: bold;
#                     height: 2.5em;
#                     width: 8em;
#                     cursor: pointer;
#                     round: 2px;
#                     }

#                     .btn_add :hover {
#                     background-color: #05d588;
#                     }
#                     </style>
#                     <button id='click-button'
#                         class="btn_add"
#                         >&CirclePlus; Add</button>
#                 </span>
#             `;
#             }

#             getGui() {
#                 return this.eGui;
#             }

#         };
#         """
#     )

#     cell_button_delete = JsCode(
#         """
#     class BtnCellRenderer {
#         init(params) {
#             this.params = params;
#             this.eGui = document.createElement('div');
#             this.eGui.innerHTML = `
#             <span>
#                 <style>
#                 .btn {
#                 background-color: #F94721;
#                 border: none;
#                 color: white;
#                 font-size: 10px;
#                 font-weight: bold;
#                 height: 2.5em;
#                 width: 8em;
#                 cursor: pointer;
#                 round: 2px;
#                 }

#                 .btn:hover {
#                 background-color: #FB6747;
#                 }
#                 </style>
#                 <button id='click-button'
#                     class="btn"
#                     >&#128465; Delete</button>
#             </span>
#         `;
#         }

#         getGui() {
#             return this.eGui;
#         }

#     };
# """
#     )

#     def addrow_handler():
#         JsCode(string_to_add_row)


#     gb.configure_column(
#         "",
#         headerTooltip="Click on Button to add new row",
#         editable=False,
#         filter=False,
#         onCellClicked=addrow_handler(),
#         cellRenderer=cell_button_add,
#         autoHeight=True,
#         wrapText=True,
#         lockPosition="left",
#     )
#     gb.configure_column(
#         "Type",
#         cellEditor="agSelectCellEditor",
#         cellEditorParams={"values": schema_types},
#         editable=True,
#     )
#     gb.configure_column(
#         "Delete",
#         headerTooltip="Click on Button to remove row",
#         editable=False,
#         filter=False,
#         onCellClicked=JsCode(string_to_delete),
#         cellRenderer=cell_button_delete,
#         autoHeight=True,
#         suppressMovable="true",
#     )

#     gb.configure_default_column(editable=True)
#     gb.configure_selection(use_checkbox=True, selection_mode="multiple")
#     grid_options = gb.build()
#     grid_return = AgGrid(
#         st.session_state.test,
#         gridOptions=grid_options,
#         allow_unsafe_jscode=True,
#         theme="streamlit",
#         update_mode=GridUpdateMode.VALUE_CHANGED,
#     )
#     st.session_state.test = pd.DataFrame(grid_return["data"]).sort_index()


# schema_container()
# st.write(st.session_state.test)

# if "schema" not in st.session_state:
#     st.session_state.schema = pd.DataFrame(
#         [["", "", ""]],
#         columns=["Column Name", "Units (e.g.lbs, kg, MM/dd/yyyy)", "Type"],
#     )

# def add_schema_row():
#     df = st.session_state.schema
#     print("len before:", len(df))

#     new_row = pd.Series(["", "", ""], index=df.columns)

#     df.loc[len(df)] = new_row
#     st.session_state.schema = df

#     print("len after:", len(st.session_state.schema))

# add_row_button = st.button("➕ Add Row")

# if add_row_button:
#     add_schema_row()

# col1, col2 = st.columns([0.7, 0.3])

# gb = GridOptionsBuilder.from_dataframe(st.session_state.schema)
# gb.configure_column("Column Name", editable=True)
# gb.configure_column("Units (e.g.lbs, kg, MM/dd/yyyy)", editable=True)
# gb.configure_column(
#     "Type",
#     cellEditor='agSelectCellEditor', cellEditorParams={'values': schema_types },
#     editable=True,
# )
# gb.configure_column(
#     "Remove",
#     cellEditor='agSelectCellEditor',
#     editable=False,
# )
# go = gb.build()
# response = AgGrid(
#     st.session_state.schema,
#     gridOptions=go,
#     reload_data=False,
#     update_mode=GridUpdateMode.VALUE_CHANGED,
#     data_return_mode=DataReturnMode.AS_INPUT
# )
# st.session_state.schema = response['data']


# # Function to create the AgGrid table
# def create_grid(df):
#     gb = GridOptionsBuilder.from_dataframe(df)
#     gb.configure_column("Column Name", editable=True)
#     gb.configure_column("Units (e.g.lbs, kg, MM/dd/yyyy)", editable=True)
#     gb.configure_column(
#         "Type",
#         cellEditor="agSelectCellEditor",
#         cellEditorParams={"values": schema_types},
#         editable=True,
#     )
#     gb.configure_selection(selection_mode="multiple", use_checkbox=True)
#     gridOptions = gb.build()
#     grid = AgGrid(
#         df,
#         gridOptions=gridOptions,
#         fit_columns_on_grid_load=True,
#         height=500,
#         width="100%",
#         theme="streamlit",
#         update_mode=GridUpdateMode.VALUE_CHANGED,
#         data_return_mode=DataReturnMode.AS_INPUT,
#         reload_data=False,
#         allow_unsafe_jscode=True,
#     )
#     return grid


# if "schema" not in st.session_state:
#     st.session_state.schema = pd.DataFrame(
#         [["", "", ""]],
#         columns=["Column Name", "Units (e.g.lbs, kg, MM/dd/yyyy)", "Type"],
#     )

# # Schema types for dropdown
# schema_types = ["Integer", "Varchar", "String", "Float", "Category"]

# # Add and Delete Row Buttons


# # Create the grid and capture the response
# grid_response = create_grid(st.session_state.schema)

# # Update session state schema with the latest data from the grid
# st.session_state.schema = pd.DataFrame(grid_response["data"])
# st.write(st.session_state.schema)

# # Schema types for dropdown
# # schema_types = ["Integer", "Varchar", "String", "Float", "Category"]

# # # Add and Delete Row Buttons
# # add_row_button = st.button("➕ Add Row")
# # delete_row_button = st.button("➖ Delete Row")

# # If the Add Row button is clicked, add a new row and rerun
# # if add_row_button:
# #     st.session_state.schema = add_schema_row(st.session_state.schema)

# # # Create the grid and capture the response
# # st.session_state.schema = create_grid(st.session_state.schema)

# # If the Delete Row button is clicked, delete the selected rows and rerun
# # def delete_schema_row(df, selected_rows):
# #     if selected_rows:
# #         selected_indices = [row['_selectedRowNodeInfo']['nodeRowIndex'] for row in selected_rows]
# #         df = df.drop(df.index[selected_indices])
# #         df.reset_index(drop=True, inplace=True)  # Reset index after dropping rows
# #     return df

# # if delete_row_button:
# #     st.session_state.schema = delete_schema_row(st.session_state.schema, st.session_state.schema['selected_rows'])


st.subheader("Data Schema")

def del_row(row_index, i):
    if len(st.session_state.category_schema[row_index]) > i:
        st.session_state.category_schema[row_index].pop(i)


def add_row(row_index):
    st.session_state.category_schema[row_index].append("")


html_contents = """
<script defer>
const fakeButton = window.parent.document.querySelector("[data-testid^='baseButton-secondary']");
const tbl = window.parent.document.querySelector("[data-testid^='stDataFrameResizable']");
const canvas = window.parent.document.querySelector("[data-testid^='data-grid-canvas']");
let sortedBy = 1
function sendPayload(obj) {
    payloadStr = JSON.stringify(obj);
    window.sessionStorage.setItem("payload", payloadStr);
    fetch('/js_callback', {
        method: 'POST',
        body: payloadStr,
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        fakeButton.click();
    });    
}
function updateColumnValue() {
    const headers = canvas.querySelectorAll('th[role="columnheader"]');
    let arrowFound = false;
    
    headers.forEach(header => {
        const textContent = header.textContent.trim();
        const colIndex = parseInt(header.getAttribute('aria-colindex'), 10);
        if (textContent.startsWith('↑')) {
            sortedBy = colIndex;
            arrowFound = true;
        } else if (textContent.startsWith('↓')) {
            sortedBy = -colIndex;
            arrowFound = true;
        }
    });
    if (!arrowFound) {
        sortedBy = 1;
    }    
    console.log(`Sorting column is now: ${sortedBy}`);
}
const sortObserver = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
        if (mutation.type === 'characterData' || mutation.type === 'childList') {
            updateColumnValue();
        }
    });
}); 
// Observe changes in the canvas element and its subtree
sortObserver.observe(canvas, {
    characterData: true,
    childList: true,
    subtree: true
});
function handleTableClick(event) {
    // MutationObserver callback function
    const cellObserverCallback = (mutationsList, observer) => {
        for (const mutation of mutationsList) {
            if (mutation.type === 'attributes' && mutation.attributeName === 'aria-selected') {
                const target = mutation.target;
                if (target.tagName === 'TD' && target.getAttribute('aria-selected') === 'true') {
                    cellCoords = target.id.replace('glide-cell-','').replace('-',',');
                    console.log(`Detected click on cell {${cellCoords}}, sorted by column "${sortedBy}"`);
                    observer.disconnect(); // Stop observing once the element is found                    
                    sendPayload({"action": "click", "cellId": cellCoords, "sortedByCol": sortedBy});                    
                }
            }
        }
    };
    // Create a MutationObserver
    const cellObserver = new MutationObserver(cellObserverCallback);  
    // Observe changes in attributes in the subtree of the canvas element
    cellObserver.observe(canvas, { attributes: true, subtree: true });
}
tbl.addEventListener('click', handleTableClick)
console.log("Event listeners added!");
</script>
"""

if "category_schema" not in ss:
    st.session_state.category_schema = {}


def data_schema_container():
    if "table_name" not in st.session_state:
        st.session_state["table_name"] = ""

    st.session_state.table_name = st.text_input("Table Name")

    if "last_active_category_index" not in st.session_state:
        st.session_state.last_active_category_index = 0
    if "selected_category_index" not in st.session_state:
        st.session_state.selected_category_index = 0

    if "user_input" not in st.session_state:
        st.session_state.user_input = pd.DataFrame()
    if "previous_df" not in st.session_state:
        st.session_state.previous_df = pd.DataFrame([])

    col1, col2 = st.columns([0.7, 0.3])
    df = pd.DataFrame(
        columns=["Column Name", "Units (e.g.lbs, kg, MM/dd/yyyy)", "Type"]
    )
    numbers = ["Integer", "Varchar", "String", "Float", "Category"]

    st.session_state.user_input = col1.data_editor(
        df,
        column_config={
            "Type": st.column_config.SelectboxColumn(
                "Type",
                options=numbers,
                default="Integer",
            ),
            "Column Name": st.column_config.TextColumn(),
            "Units (e.g.lbs, kg, MM/dd/yyyy)": st.column_config.TextColumn(),
        },
        num_rows="dynamic",
        hide_index=True,
        use_container_width=True,
        key="DATAFRAME",
    )

    st.text_input(
        label="N/A",
        label_visibility="hidden",
        key="CELL_ID",
        disabled=True,
        help="Click on a cell...",
    )

    # Create a fake button:
    st.button("", key="fakeButton", on_click=fake_click)
    st.markdown(
        """
        <style>
        button, iframe {
            visibility: hidden;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    html(html_contents)

    for index, entry in enumerate(st.session_state.user_input["Type"]):
        if entry == "Category":
            column_name = st.session_state.user_input["Column Name"]
            if st.session_state.category_schema.get(index) == None:
                st.session_state.category_schema[index] = []

            col2.markdown(f"##### {column_name.iloc[index]}:")
            if col2.button("Add Row", key=f"add_row_{index}"):
                add_row(index)

            for i in range(len(st.session_state.category_schema[index])):
                sub_col1, sub_col2 = col2.columns([0.1, 0.9])
                st.session_state.category_schema[index][i] = sub_col2.text_input(
                    "",
                    label_visibility="collapsed",
                    value=st.session_state.category_schema[index][i],
                    key=f"Category Input Box_{index}_{i}",
                )
                if sub_col1.button("X", key=f"del_row_{index}_{i}"):
                    del_row(index, i)
                    st.rerun()

    # st.write(st.session_state.category_schema)
    # st.write(st.session_state.user_input)

    column_name = st.session_state.user_input.get("Column Name", "")
    if "column name" not in st.session_state:
        st.session_state["column name"] = ""

    if "user input" not in st.session_state:
        st.session_state["user input"] = ""


data_schema_container()
st.divider()

validation_css = {
    True: """
            {
                background-color: #FFFFF;
                border-radius: 10px;
                padding: 15px;
            }
            """,
    False: """
            {
                background-color: #f8d7da;
                border-radius: 10px;
                padding: 15px;
            }
            """,
}

# *´:°•.°+.*•´.*:˚.°*.˚•´.°:°•.°•.*•´.*:˚.°*.˚•´.°:°•.°+.*•´.*:*//
# *                          THREAT MODEL                      *//
# *.•°:°.´+˚.*°.˚:*.´•*.+°.•°:´*.´•*.•°.•°:°.´:•˚°.*°.˚:*.´+°.•*//

# ********** SESSION INITILIAZARION **********
if "threat_model" not in st.session_state:
    st.session_state["threat_model"] = ""
if "selected_providers" not in st.session_state:
    st.session_state.selected_providers = []
if "cloud provider" not in st.session_state:
    st.session_state["cloud provider"] = ""
if "isvalid_threat_model" not in st.session_state:
    st.session_state["isvalid_threat_model"] = 1
if "isvalid_analysis_details" not in st.session_state:
    st.session_state["isvalid_analysis_details"] = 1
if "isvalid_sql" not in st.session_state:
    st.session_state["isvalid_sql"] = True

st.subheader("Threat Model")


def threat_model_container() -> None:

    cloud_providers = [
        "AWS",
        "Microsoft Azure",
        "Google Cloud",
        "Chameleon Open Cloud",
        "Cloud 1",
        "Cloud 2",
    ]
    threat_models = ["Semi-Honest", "Malicious"]
    css_styles = validation_css[st.session_state["isvalid_threat_model"] == 1]
    with stylable_container(
        key="thread_model",
        css_styles=css_styles,
    ):
        col1, col2 = st.columns(2)
        new_threat_model = col1.radio(
            "Threat Model",
            options=threat_models,
            label_visibility="collapsed",
            key="t1",
        )

        # Detect if the threat model has been changed
        if new_threat_model != st.session_state.get("threat_model", ""):
            st.session_state.threat_model = new_threat_model
            st.session_state.threat_model_changed = True
        else:
            st.session_state.threat_model_changed = False

        col2.markdown("##### Cloud Providers")

        if st.session_state.threat_model_changed:
            if st.session_state.threat_model == "Semi-Honest":
                st.session_state.selected_providers = random.sample(cloud_providers, 3)

            elif st.session_state.threat_model == "Malicious":
                st.session_state.selected_providers = random.sample(cloud_providers, 4)

        # Add or remove providers based on toggle state
        for _, provider in enumerate(cloud_providers):
            is_selected = col2.toggle(
                provider,
                key=f"toggle_{provider}",
                value=provider in st.session_state.selected_providers,
            )

            if is_selected and provider not in st.session_state.selected_providers:
                st.session_state.selected_providers.append(provider)
            elif not is_selected and provider in st.session_state.selected_providers:
                st.session_state.selected_providers.remove(provider)
    if st.session_state["isvalid_threat_model"] == 2:
        st.error(
            "Error: In the Semi-Honest threat model, you must select at least 3 cloud providers."
        )
    elif st.session_state["isvalid_threat_model"] == 3:
        st.error(
            "Error: In the Malicious threat model, you must select at least 4 cloud providers."
        )


threat_model_container()
st.write(st.session_state.selected_providers)
st.divider()

# *´:°•.°+.*•´.*:˚.°*.˚•´.°:°•.°•.*•´.*:˚.°*.˚•´.°:°•.°+.*•´.*:*//
# *                       ANALYSIS DETAILS                     *//
# *.•°:°.´+˚.*°.˚:*.´•*.+°.•°:´*.´•*.•°.•°:°.´:•˚°.*°.˚:*.´+°.•*//

st.subheader("Analysis Details")

type_mapping = {
    "String": "TEXT",
    "Integer": "INT",
    "Float": "FLOAT",
    "Boolean": "BOOLEAN",
}


def create_table_sql() -> str:
    table_name = st.session_state.table_name
    columns = st.session_state.user_input.iloc[:, 0]
    types = st.session_state.user_input.iloc[:, 2]

    create_table_sql = f"CREATE TABLE {table_name} (\n"

    # Iterate through columns and types to create the column definitions
    for column, data_type in zip(columns, types):
        data_type = type_mapping[data_type]
        create_table_sql += f"    {column} {data_type},\n"

    create_table_sql = create_table_sql.rstrip(",\n") + "\n);"
    return str(create_table_sql)


def drop_table_sql() -> str:
    table_name = st.session_state.table_name
    sql = f"DROP TABLE IF EXISTS {table_name};"
    return sql


def validate_sql():
    # conn = st.connection(
    #     "verification",
    #     type="sql",
    #     autocommit=True,
    #     username="user1",
    #     password="Adam0511!",
    #     host="localhost",
    #     database="verification",
    #     dialect="mysql",
    # )
    engine = create_engine(
        f"mysql+mysqlconnector://user1:Adam0511!@localhost/verification"
    )
    create_sql = create_table_sql()
    query = st.session_state.query
    drop_sql = drop_table_sql()
    try:
        with engine.connect() as conn:
            # Execute the create table query
            conn.execute(sqlalchemy.text(drop_sql))
            conn.execute(sqlalchemy.text(create_sql))
            conn.execute(sqlalchemy.text(query))
            conn.execute(sqlalchemy.text(drop_sql))
            return True
    except Exception as e:
        print(e)
        return False


def analysis_details_container() -> None:
    with stylable_container(
        key="analysis_details_model",
        css_styles=validation_css[
            st.session_state.get("isvalid_analysis_details", 1) == 1
        ],
    ):
        st.session_state.query_name = st.text_input("Query Name")

        if "query_name" not in st.session_state:
            st.session_state["query_name"] = ""

        st.session_state.query = st.text_area("Input Query Here")
        if "query" not in st.session_state:
            st.session_state["query"] = ""

        st.session_state.description = st.text_area("Description")
        if "description" not in st.session_state:
            st.session_state["description"] = ""

    if st.session_state.isvalid_analysis_details == 2:
        st.error("Error: No fields should be empty.")
    elif st.session_state.isvalid_analysis_details == 3:
        st.error("Error: Invalid SQL query.")


analysis_details_container()

st.write(
    [
        st.session_state["query_name"],
        st.session_state["query"],
        st.session_state["description"],
    ]
)
st.divider()

if "Submit" not in st.session_state:
    st.session_state["Submit"] = False

st.subheader("Complete Registration")
st.session_state.submitted = st.button("Submit")


# *´:°•.°+.*•´.*:˚.°*.˚•´.°:°•.°•.*•´.*:˚.°*.˚•´.°:°•.°+.*•´.*:*//
# *                       INPUT VALIDATION                     *//
# *.•°:°.´+˚.*°.˚:*.´•*.+°.•°:´*.´•*.•°.•°:°.´:•˚°.*°.˚:*.´+°.•*//
def validate_threat_model() -> bool:
    if st.session_state.threat_model == "Semi-Honest":
        if len(st.session_state.selected_providers) >= 3:
            st.session_state.isvalid_threat_model = 1
            st.success("Success")
            return True
        elif len(st.session_state.selected_providers) < 3:
            st.session_state.isvalid_threat_model = 2
            return False
    if st.session_state.threat_model == "Malicious":
        if len(st.session_state.selected_providers) >= 4:
            st.session_state.isvalid_threat_model = 1
            st.success("Success")
            return True
        elif len(st.session_state.selected_providers) < 4:
            st.session_state.isvalid_threat_model = 3
            return False


def validate_analysis_details() -> bool:
    if (
        st.session_state["query_name"] == ""
        or st.session_state["query"] == ""
        or st.session_state["description"] == ""
    ):
        st.session_state["isvalid_analysis_details"] = 2
        return False
    else:
        isValid = validate_sql()
        if isValid:
            st.session_state["isvalid_analysis_details"] = 1
        else:
            st.session_state["isvalid_analysis_details"] = 3
        return True


if st.session_state.submitted:
    if "disabled" not in st.session_state:
        st.session_state["disabled"] = False

    def disable():
        st.session_state["disabled"] = True

    disable()
    st.session_state["query_name"] = st.session_state.query_name
    st.session_state["description"] = st.session_state.description
    st.session_state["query"] = st.session_state.query
    st.session_state["threat model"] = st.session_state.threat_model
    st.session_state["category schema"] = st.session_state.category_schema
    st.session_state["user input"] = st.session_state.user_input
    st.session_state["Submit"] = st.session_state.submitted

    if validate_threat_model() and validate_analysis_details():
        pass

    st.rerun()

st.write(st.session_state)

if __name__ == "__main__":
    if "__streamlitmagic__" not in locals():
        # Code adapted from bootstrap.py in streamlit
        streamlit.web.bootstrap._fix_sys_path(__file__)
        streamlit.web.bootstrap._fix_tornado_crash()
        streamlit.web.bootstrap._fix_sys_argv(__file__, [])
        streamlit.web.bootstrap._fix_pydeck_mapbox_api_warning()
        streamlit.web.bootstrap._fix_pydantic_duplicate_validators_error()
        # streamlit.web.bootstrap._install_pages_watcher(__file__)

        server = CustomServer(__file__, is_hello=False)

        async def run_server():
            await server.start()
            streamlit.web.bootstrap._on_server_start(server)
            streamlit.web.bootstrap._set_up_signal_handler(server)
            await server.stopped

        asyncio.run(run_server())
