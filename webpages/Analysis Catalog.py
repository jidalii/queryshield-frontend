from datetime import datetime
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import pytz

from components.analysis_catalog_component import analysis_catalog_component
from utils.db.db_services import fetch_all_analysis_catalog
from utils.share_data_validation import validate_share_data, validate_share_data_file
from components.sidebar_login_component import sidebar_login_component,email_form, signup_form

st.title("Analysis Catalog")

engine = create_engine(
    "postgresql+psycopg2://user1:12345678!@localhost:5432/queryshield"
)


# Convert the dictionary into a Pandas DataFrame
query_result = fetch_all_analysis_catalog(engine)
# print("query_result", query_result[0])
# print("query_result", type(query_result[0]))
# print("Column names:", query_result[0]._fields)
# column_names = list(query_result[0]._fields)
column_names = list(query_result[0].keys())
boston_tz = pytz.timezone('America/New_York')
    
processed_result = []
for analysis in query_result:
    # Convert time_created to Boston timezone and format it
    time_created = analysis['time_created'].astimezone(boston_tz).strftime('%Y:%m:%d %H:%M')

    # Create a dictionary with modified time_created
    processed_row = {
        'aid': analysis['aid'],
        'analysis_name': analysis['analysis_name'],
        'analyst_name': analysis['analyst_name'],
        'analyst_id': analysis['analyst_id'],
        'time_created': time_created,  # modified time_created
        'details': analysis['details'],
        'status': analysis['status'],
        'owners_count': analysis['owners_count'],
    }
    
    processed_result.append(processed_row)
    
df = pd.DataFrame(processed_result)

analysis_catalog_component(df)


