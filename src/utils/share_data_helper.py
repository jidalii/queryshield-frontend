import streamlit as st
import pandas as pd
import time
from utils.auth.jwt_token import validate_data_share_access
from db.db_services import fetch_single_analysis
from db.db_services import register_data_owner
from configs.configs import TIMEZONE


def _validate_column_type(column, dtype):
    try:
        if dtype == "Integer":
            return (pd.to_numeric(column, errors="coerce").notna().all(),)
        elif dtype == "Float":
            return pd.to_numeric(column, errors="coerce").notna().all()
        elif dtype in ["String", "Varchar"]:
            return all(isinstance(value, str) for value in column)
        elif dtype == "Category":
            return all(isinstance(str(value), str) for value in column)
        else:
            raise ValueError(f"Unsupported type: {dtype}")
    except Exception as e:
        err = f"Error in column {column.name}: {e}"
        print(err)
        return False


def check_query_params() -> str:
    """
    Checks if the required query parameters 'aid' and 'jwt' are present in the URL.
    Displays an error message if any of the parameters are missing.
    """
    if "aid" not in st.query_params:
        st.error("Missing Analysis ID in the URL")
    if "jwt" not in st.query_params:
        st.error("Missing JWT in the URL")


def initialize_user() -> None:
    """
    Initializes the user session by validating the JWT token from the query parameters.
    If the token is valid, sets the session state with the user's information.
    """
    st.session_state["jwt_token"] = st.query_params["jwt"]
    ok, payload = validate_data_share_access(st.query_params["jwt"])
    if ok:
        st.session_state["logined"] = True
        st.session_state["user"] = payload["user"]
    else:
        st.error("Invalid Access Token")
        st.stop()


def initialize_session_state(names: list) -> None:
    if "view_category_df" not in st.session_state:
        st.session_state["view_category_df"] = {}
    if "data_to_share" not in st.session_state:
        st.session_state["data_to_share"] = pd.DataFrame(columns=names)


def fetch_analysis_data(engine) -> dict:
    analysis = fetch_single_analysis(engine, st.query_params["aid"])
    time_created = (
        analysis["time_created"].astimezone(TIMEZONE).strftime("%Y:%m:%d %H:%M")
    )
    return {
        "aid": analysis["aid"],
        "analysis_name": analysis["analysis_name"],
        "time_created": time_created,
        "details": analysis["details"],
        "status": analysis["status"],
    }


def handle_submission(engine, names, dtypes, replication_factor) -> None:
    """
    Handles the submission process, including data validation, user registration,
    and replication factor checks.
    """

    def validate_share_data_file(data_df, names, column_types):
        if len(data_df.columns) != len(names):
            err = f"Column count mismatch: DataFrame has {len(data_df.columns)} columns, expected {len(names)}."
            return False, err
        for col_name, expected_name in zip(data_df.columns, names):
            if col_name != expected_name:
                err = f"Column name mismatch: Found '{col_name}', expected '{expected_name}'."
                return False, err
        for column_name, dtype in zip(data_df.columns, column_types):
            if not _validate_column_type(data_df[column_name], dtype):
                print(data_df[column_name])
                err = f"Invalid data in column '{column_name}' of expected type '{dtype}'."
                return False, err
        return True, None

    is_valid, err = validate_share_data_file(
        st.session_state["data_to_share"], names, dtypes
    )
    if not is_valid:
        st.error(f"Error: {err}")
        return

    aid = st.query_params.get("aid")
    uid = st.session_state["user"]["uid"]

    if not aid or not uid:
        st.error("Error: Missing required parameters")
        return

    if is_registered_owner(engine, aid, uid):
        st.error("Error: you have already registered for this analysis")
        return

    success, err = register_data_owner(engine, aid, uid)
    if not success:
        st.error(f"Error: {err}")
        return

    if replication_factor == -1:
        st.error("Error: invalid threat model")
        return

    time.sleep(1)
    st.success("Success")
