import asyncio
import json
import random

import streamlit as st
import pandas as pd

from streamlit_extras.stylable_container import stylable_container
from streamlit.components.v1 import html

from multiprocessing.shared_memory import SharedMemory

from sqlalchemy import create_engine

from utils.auth.email_auth import login_handler, signup_handler
from models.auth import UserRegistration, UserLogin
from models.analysis import *
from components.create_analysis.threat_model_component import threat_model_component, analysis_details_component
from utils.db.schema_validation import *
from utils.db.db_services import *
from utils.row_detection import *
from configs.configs import SCHEMA_TYPES, CLOUD_PROVIDERS, THREAT_MODELS, TYPE_MAPPING
from configs.html import VALIDATION_CSS, HTML_CONTENTS
from components.sidebar_login_component import (
    sidebar_login_component,
)

st.set_page_config(
    page_title="QueryShield",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.sidebar.title("QueryShield")

engine = create_engine(
    "postgresql+psycopg2://user1:12345678!@localhost:5432/queryshield"
)

if "logined" not in st.session_state:
    st.session_state["logined"] = False

sidebar_login_component(engine)

if "disabled" not in st.session_state:
    st.session_state["disabled"] = False


def disable():
    st.session_state["disabled"] = True


def submit_btn():
    return st.button("Submit")


st.title("Create New Analysis")
if "user" in st.session_state:
    _user = st.session_state["user"]
    st.write(f"User: {_user}")

_JS_TO_PD_COL_OFFSET: int = -2

# Create shared memory for the payload
try:
    payload_memory = SharedMemory(name="JS_PAYLOAD", create=True, size=128)
except FileExistsError:
    payload_memory = SharedMemory(name="JS_PAYLOAD", create=False, size=128)

# *´:°•.°+.*•´.*:˚.°*.˚•´.°:°•.°•.*•´.*:˚.°*.˚•´.°:°•.°+.*•´.*:*//
# *                          DATA SCHEMA                       *//
# *.•°:°.´+˚.*°.˚:*.´•*.+°.•°:´*.´•*.•°.•°:°.´:•˚°.*°.˚:*.´+°.•*//

st.subheader("Data Schema")
if "table_name" not in st.session_state:
    st.session_state["table_name"] = ""
if "cell_position" not in st.session_state:
    st.session_state["cell_position"] = (0, 0)

if "create_analysis_input" not in st.session_state:
    st.session_state["create_analysis_input"] = {}

create_analysis_input = st.session_state["create_analysis_input"]

if "table_name" not in create_analysis_input:
    create_analysis_input["table_name"] = ""


create_analysis_input["table_name"] = st.text_input(
    "Table Name", create_analysis_input["table_name"]
)

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

df = pd.DataFrame(columns=["name", "units", "type"])
if "last_user_input" in create_analysis_input and (
    st.session_state["user_input_changed"] == 0
    or st.session_state["user_input_changed"] == 1
):
    df = create_analysis_input["last_user_input"].reset_index(drop=True)

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


def schema_container():
    col1, col2 = st.columns([0.7, 0.3])

    conlumn_config = {
        "type": st.column_config.SelectboxColumn(
            "Type",
            options=SCHEMA_TYPES,
            default="Integer",
        ),
        "name": st.column_config.TextColumn("Column Name"),
        "units": st.column_config.TextColumn("Units (e.g.lbs, kg, MM/dd/yyyy)"),
    }
    create_analysis_input["user_input"] = col1.data_editor(
        df,
        column_config=conlumn_config,
        num_rows="dynamic",
        hide_index=True,
        use_container_width=True,
        # on_change=update_user_input_changed()
    )

    st.session_state.schema_types = create_analysis_input["user_input"]["type"].tolist()
    if "category_df" not in st.session_state:
        st.session_state.category_df = {}

    if "active_category" not in st.session_state:
        st.session_state.active_category = [False, -1]

    def store_df(index):
        if str(index) in st.session_state.category_df:
            st.session_state.category_df[index] = create_analysis_input[
                "category_schema"
            ][index].reset_index(drop=True)

    for index, entry in enumerate(create_analysis_input["user_input"]["type"]):
        if (
            entry == "Category" or entry not in SCHEMA_TYPES
        ) and index == st.session_state["cell_position"][0]:
            st.session_state.active_category = [True, index]
            if index not in st.session_state.category_df:
                print("category_df not found")
                st.session_state.category_df[index] = pd.DataFrame(columns=["Category"])

            height = 5 + 35 * index
            col2.html(f"<p style='height: {height}px;'></p>")
            create_analysis_input["category_schema"][index] = col2.data_editor(
                st.session_state.category_df[index],
                column_config={
                    "Category": st.column_config.TextColumn(),
                },
                num_rows="dynamic",
                hide_index=True,
                use_container_width=True,
                # on_change=store_df(index),
            )

            st.session_state.category_df[index] = create_analysis_input[
                "category_schema"
            ][index].reset_index(drop=True)

schema_container()

# # Create a fake button:
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
    </style>
    """,
    unsafe_allow_html=True,
)
html(HTML_CONTENTS)

st.write(f"position: {st.session_state.cell_position}")
st.write(create_analysis_input)
st.write(create_analysis_input["category_schema"])
st.write(st.session_state.schema_types)

column_name = create_analysis_input["user_input"].get("Column Name", "")

st.divider()

# *´:°•.°+.*•´.*:˚.°*.˚•´.°:°•.°•.*•´.*:˚.°*.˚•´.°:°•.°+.*•´.*:*//
# *                          THREAT MODEL                      *//
# *.•°:°.´+˚.*°.˚:*.´•*.+°.•°:´*.´•*.•°.•°:°.´:•˚°.*°.˚:*.´+°.•*//

# ********** SESSION INITILIAZARION **********
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

st.subheader("Threat Model")

threat_model_component()
# st.write(create_analysis_input["selected_providers"])
st.divider()

# *´:°•.°+.*•´.*:˚.°*.˚•´.°:°•.°•.*•´.*:˚.°*.˚•´.°:°•.°+.*•´.*:*//
# *                       ANALYSIS DETAILS                     *//
# *.•°:°.´+˚.*°.˚:*.´•*.+°.•°:´*.´•*.•°.•°:°.´:•˚°.*°.˚:*.´+°.•*//

st.subheader("Analysis Details")

if "query_name" not in create_analysis_input:
    create_analysis_input["query_name"] = ""
if "query" not in create_analysis_input:
    create_analysis_input["query"] = ""
if "description" not in create_analysis_input:
    create_analysis_input["description"] = ""

analysis_details_component()
# st.write(
#     [
#         create_analysis_input["query_name"],
#         create_analysis_input["query"],
#         create_analysis_input["description"],
#     ]
# )
st.divider()

if "Submit" not in st.session_state:
    st.session_state["Submit"] = False

st.subheader("Complete Registration")
st.session_state.submitted = st.button("Submit")


# *´:°•.°+.*•´.*:˚.°*.˚•´.°:°•.°•.*•´.*:˚.°*.˚•´.°:°•.°+.*•´.*:*//
# *                       INPUT VALIDATION                     *//
# *.•°:°.´+˚.*°.˚:*.´•*.+°.•°:´*.´•*.•°.•°:°.´:•˚°.*°.˚:*.´+°.•*//
def validate_threat_model() -> bool:
    if create_analysis_input["threat_model"] == "Semi-Honest":
        if len(create_analysis_input["selected_providers"]) == 3:
            st.session_state.isvalid_threat_model = 1
            return True
        elif len(create_analysis_input["selected_providers"]) <= 3:
            st.session_state.isvalid_threat_model = 2
            return False
    if create_analysis_input["threat_model"] == "Malicious":
        if len(create_analysis_input["selected_providers"]) == 4:
            st.session_state.isvalid_threat_model = 1
            return True
        elif len(create_analysis_input["selected_providers"]) <= 4:
            st.session_state.isvalid_threat_model = 3
            return False
    return False


def validate_analysis_details() -> bool:
    if (
        create_analysis_input["query_name"] == ""
        or create_analysis_input["query"] == ""
        or create_analysis_input["description"] == ""
    ):
        st.session_state["isvalid_analysis_details"] = 2
        return False
    else:
        isValid = validate_sql(TYPE_MAPPING)
        if isValid:
            st.session_state["isvalid_analysis_details"] = 1
            return True
        else:
            st.session_state["isvalid_analysis_details"] = 3
            return False


def data2json():
    # handle data schema
    result_dict = {}
    result_dict["schema"] = {}
    schema = create_analysis_input["user_input"]
    category_schema = create_analysis_input["category_schema"]
    for i, row in schema.iterrows():
        print(row)
        field = row["name"]
        field_type = row["type"]
        field_data = {"units": row["units"], "type": field_type}

        # If the field type is "Category", map it to category_schema
        if field_type == "Category":
            field_data["categories"] = category_schema[i]["Category"].tolist()

        result_dict["schema"][field] = field_data
    # handle threat model and providers
    result_dict["threat_model"] = create_analysis_input["threat_model"]
    result_dict["selected_providers"] = create_analysis_input["selected_providers"]
    result_dict["query"] = create_analysis_input["query"]
    result_dict["description"] = create_analysis_input["description"]

    for key, value in result_dict.items():
        if isinstance(value, pd.DataFrame):
            result_dict[key] = value.to_dict()
    print(result_dict)

    return json.dumps(result_dict)


if st.session_state.submitted:
    if "disabled" not in st.session_state:
        st.session_state["disabled"] = False

    def disable():
        st.session_state["disabled"] = True

    disable()
    create_analysis_input["last_user_input"] = create_analysis_input["user_input"]
    st.session_state["Submit"] = st.session_state.submitted

    if validate_threat_model() and validate_analysis_details():
        st.session_state.user_input_changed = 1
        st.rerun()
    else:
        st.rerun()

if (
    st.session_state["isvalid_analysis_details"] == 1
    and st.session_state["isvalid_analysis_details"] == 1
):
    new_analysis = AnalysisCreation(
        analysis_name=create_analysis_input["query_name"],
        analyst_id=1,
        details=data2json(),
        status="Created",
    )
    isSuccess, e = insert_new_analysis(engine, new_analysis)
    if isSuccess:
        st.success("Success")
    else:
        st.error(f"DB error: {e}")


if __name__ == "__main__":
    import streamlit.web.bootstrap

    if "__streamlitmagic__" not in locals():
        # Code adapted from bootstrap.py in streamlit
        streamlit.web.bootstrap._fix_sys_path(__file__)
        streamlit.web.bootstrap._fix_tornado_crash()
        streamlit.web.bootstrap._fix_sys_argv(__file__, [])
        streamlit.web.bootstrap._fix_pydeck_mapbox_api_warning()
        # streamlit.web.bootstrap._fix_pydantic_duplicate_validators_error()

        server = CustomServer(__file__, is_hello=False)

        async def run_server():
            await server.start()
            streamlit.web.bootstrap._on_server_start(server)
            streamlit.web.bootstrap._set_up_signal_handler(server)
            await server.stopped

        asyncio.run(run_server())
