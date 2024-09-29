import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from streamlit_extras.stylable_container import stylable_container
from st_aggrid import AgGrid, GridOptionsBuilder
import sqlalchemy
from sqlalchemy import create_engine

import random

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


st.subheader("Data Schema")
# with st.form("Submit", border=False, clear_on_submit=False):
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

# AgGrid(st.session_state.user_input)


def data_editor_changed():
    user_input = st.session_state.user_input
    previous_df = st.session_state.previous_df

    for index, (row_current, row_previous) in enumerate(
        zip(user_input.iterrows(), previous_df.iterrows())
    ):
        _, current_row = row_current
        _, previous_row = row_previous
        if not current_row.equals(previous_row):
            if current_row.iloc[-1] != previous_row.iloc[-1]:
                st.session_state.last_active_category_index = index

    # Update the previous_df with the current state
    st.session_state.previous_df = user_input.copy()
    st.write(st.session_state.last_active_category_index)


col1, col2 = st.columns([0.7, 0.3])
df = pd.DataFrame(columns=["Column Name", "Units (e.g.lbs, kg, MM/dd/yyyy)", "Type"])
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
    on_change=data_editor_changed,
)

if "category_schema" not in st.session_state:
    st.session_state.category_schema = {}


def del_row(row_index, i):
    if len(st.session_state.category_schema[row_index]) > i:
        st.session_state.category_schema[row_index].pop(i)


def add_row(row_index):
    st.session_state.category_schema[row_index].append("")


for index, entry in enumerate(st.session_state.user_input["Type"]):
    if entry == "Category":
        column_name = st.session_state.user_input["Column Name"]
        if st.session_state.category_schema.get(index) == None:
            st.session_state.category_schema[index] = []

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
        # column_name = st.session_state.user_input["Column Name"][index]

        # # Determine if this entry is selected and highlight the cell if necessary
        # cell_style = "selected-cell" if st.session_state.selected_category_index == index else ""

        # # Create a button-like cell for each type, when clicked it will show the Category editor
        # if st.button(f"{entry}", key=f"type_button_{index}"):
        #     if entry == "Category":
        #         st.session_state.selected_category_index = index  # Select this category for editing
        #     else:
        #         st.session_state.selected_category_index = None  # Deselect if not "Category"

        # # Display the type with conditional coloring for selected "Category"
        # st.markdown(f"<div class='{cell_style}'>{entry}</div>", unsafe_allow_html=True)

        # # If the current type is "Category" and selected, show the category editing list
        # if entry == "Category" and st.session_state.selected_category_index == index:
        #     # Initialize category_schema for each category if it doesn't exist
        #     if st.session_state.category_schema.get(index) is None:
        #         st.session_state.category_schema[index] = []

        #     st.write(f"Editing Category: {column_name}")

        #     # Add a new row button
        #     if st.button("Add Row", key=f"add_row_{index}"):
        #         add_row(index)

        #     # Creating layout for category input and delete button
        #     for i in range(len(st.session_state.category_schema[index])):
        #         sub_col1, sub_col2 = st.columns([0.1, 0.9])  # Ensure consistent layout
        #         # Text input for each category schema entry in sub_col2
        #         st.session_state.category_schema[index][i] = sub_col2.text_input(
        #             "",
        #             label_visibility="collapsed",
        #             value=st.session_state.category_schema[index][i],
        #             key=f"Category Input Box_{index}_{i}",
        #         )
        #         # Delete button for each row in sub_col1
        #         if sub_col1.button("X", key=f"del_row_{index}_{i}"):
        #             del_row(index, i)


st.write(st.session_state.category_schema)
st.write(st.session_state.user_input)
st.write(st.session_state.previous_df)


# if any(st.session_state.user_input["Type"] == "Category"):
# df= pd.DataFrame(columns=[st.session_state.user_input["Column Name"]])
# st.data_editor(df, num_rows="dynamic", use_container_width=True )

# col1, col2= st.columns(2)
# col1.text_input(f'Enter Category Name for {st.session_state.user_input['Column Name']}')
# @st.experimental_dialog(f'Enter Categories')
# def specify():
# if st.session_state.user_input['Column Name'] not in st.session_state:
# st.session_state.user_input['Column Name']=''
# df=pd.DataFrame(columns=[st.session_state.user_input["Column Name"]])
# st.data_editor(df, num_rows="dynamic", use_container_width=True )
# confirm= st.button("Confirm", help=None)
# if confirm:
# st.button('Test')
# specify()


column_name = st.session_state.user_input.get("Column Name", "")
if "column name" not in st.session_state:
    st.session_state["column name"] = ""

if "user input" not in st.session_state:
    st.session_state["user input"] = ""

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
    st.session_state["threat model"] = ""
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
    with stylable_container(
        key="thread_model",
        css_styles=validation_css[st.session_state.isvalid_threat_model == 1],
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
    if st.session_state.isvalid_threat_model == 2:
        st.error(
            "Error: In the Semi-Honest threat model, you must select at least 3 cloud providers."
        )
    elif st.session_state.isvalid_threat_model == 3:
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
            st.session_state.isvalid_analysis_details == 1
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
