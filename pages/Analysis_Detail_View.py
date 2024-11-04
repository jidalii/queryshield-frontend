import json
import os
import threading

import streamlit as st
import pandas as pd

from dataclasses import dataclass
from itertools import chain
from multiprocessing.shared_memory import SharedMemory
from typing import Any

from sqlalchemy import create_engine
import pytz

from streamlit.components.v1 import html

from streamlit.web.server import Server
from streamlit.web.server.server import start_listening
from tornado.web import RequestHandler

from components.analysis_description_component import *
from utils.db.db_services import fetch_single_analysis

st.set_page_config("Analysis Detail View", layout="wide")

if "aid" not in st.query_params:
    st.error("Request ID should be provided.")
    st.stop()
else:
    st.session_state["analysis_id_view"] = st.query_params.aid
    st.write("analysis id: ", st.session_state["analysis_id_view"])

st.title("Analysis Detail View")

with st.sidebar:
    st.empty()

engine = create_engine(
    "postgresql+psycopg2://user1:12345678!@localhost:5432/queryshield"
)


JS_TO_PD_COL_OFFSET: int = -2

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
            f"{os.getpid()}::{threading.get_ident()}: Streamlit callback saw no payload"
        )
        return Selection(-1, -1, -1)


def _interpret_payload(payload: Selection) -> tuple[Any, Any]:
    """Interpret the payload and return the selected row and column."""
    # sorted_df = sort_df_by_selected_col(df, payload.sorted_by)
    selected_row = payload.row if payload.row >= 0 else -1
    selected_col = payload.col if payload.col >= 0 else -1

    return selected_row, selected_col


def fake_click(*args, **kwargs):
    parsed_payload: Selection = _retrieve_payload()
    selected_row, selected_col = _interpret_payload(parsed_payload)
    if selected_col != -1 or selected_row != -1:
        st.session_state["cell_position"] = selected_row, selected_col


class JSCallbackHandler(RequestHandler):
    def set_default_headers(self):
        # We hijack this method to store the JS payload
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


html_contents = """
<script defer>
const fakeButton = window.parent.document.querySelector("[data-testid^='stBaseButton-primary']");
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


schema_types = ["Integer", "Varchar", "String", "Float", "Category"]

if "view_category_df" not in st.session_state:
    st.session_state['view_category_df'] ={}

if "cell_position" not in st.session_state:
    st.session_state["cell_position"] = (0, 0)

def convert_dict_to_df(data):
    rows = []
    for key, value in data.items():
        # Note is units if available, otherwise categories if present
        note = value.get("units") if value.get("units") else ''
        rows.append({
            "name": key,
            "units": note,
            "type": value.get("type")
        })
        
    return pd.DataFrame(rows)

def convert_dict_to_category_dict(data):
    res = {}
    i =0
    for key, value in data.items():
        t = value.get("type")
        if t == 'Category':
            res[i] = value.get("categories")
        i+=1
        
    return res


analysis = fetch_single_analysis(engine, st.query_params["aid"])
# data = query_result['details']
boston_tz = pytz.timezone('America/New_York')
# Convert time_created to Boston timezone and format it
# print(analysis)
# print(analysis.keys())
time_created = analysis['time_created'].astimezone(boston_tz).strftime('%Y:%m:%d %H:%M')

# Create a dictionary with modified time_created
analysis_details = {
    'aid': analysis['aid'],
    'analysis_name': analysis['analysis_name'],
    'time_created': time_created,
    'details': analysis['details'],
    'status': analysis['status'],
}
data = analysis_details['details']
raw_schema = data['schema']
schema = convert_dict_to_df(raw_schema)
category_df = convert_dict_to_category_dict(raw_schema)

def schema_container():
    # create_analysis_input = st.session_state["create_analysis_input"]
    col1, col2 = st.columns([0.7, 0.3])
    

    df = pd.DataFrame(schema)
    col1.dataframe(df, hide_index=True, use_container_width=True)
    for index, entry in enumerate(schema["type"]):
        if (entry == "Category" or entry not in schema_types) and index == st.session_state["cell_position"][0]:
            st.session_state.active_category = [True, index]
            if index not in category_df:
                print("category_df not found")
                # st.session_state.category_df[index] = pd.DataFrame(columns=['Category'])

            height = 5 + 35 * index
            col2.html(
                f"<p style='height: {height}px;'></p>"
            )
            
            the_category_df = pd.DataFrame(category_df[index], columns=['Category'])
            col2.data_editor(
                the_category_df,
                column_config={
                    "Category": st.column_config.TextColumn(),
                    
                },
                hide_index=True,
                disabled=True
            )
    st.write(f"position: {st.session_state.cell_position}")

schema_container()

view_threat_model(data)

view_analysis_details(data)

if "query_name" in st.session_state:
    st.subheader("Data Schema")
    if "user_input" in st.session_state:
        schema_container()
        
        
    st.subheader("Threat Model")
    st.markdown(f"- {st.session_state.threat_model}")
    st.markdown("#### Cloud Provider:")
    cloud_providers = ["Google Cloud", "Microsoft Azure", "Cloud 1"]
    for provider in cloud_providers:
        st.markdown("- " + provider)
    st.subheader("Analysis Details")
    if "query_name" in st.session_state:
        st.markdown("#### Query Name:")
        st.write(f"{st.session_state.query_name}")
    if "query" in st.session_state:
        st.markdown("#### Query:")
        st.code(st.session_state.query)
    if "description" in st.session_state:
        st.markdown("#### Description:")
        st.write(f"{st.session_state.description}")

st.button("", key="fakeButton", on_click=fake_click, type="primary")
st.markdown(
    """
    <style>
    div[data-testid="stTextInput"][data-st-key="CELL_ID"] {
        visibility: hidden;
    }
    button[kind="primary"] {
        visibility: hidden;
    }
    button {
        height: 0px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
html(html_contents)