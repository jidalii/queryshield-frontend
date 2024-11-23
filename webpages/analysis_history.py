import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import pytz

from components.analysis_history_component import analysis_history_component
from utils.db.db_services import fetch_analyst_analysis_history

st.title("Analysis History")

engine = create_engine(
    "postgresql+psycopg2://user1:12345678!@localhost:5432/queryshield"
)


query_result = fetch_analyst_analysis_history(engine, 1)

boston_tz = pytz.timezone('America/New_York')
processed_result = []
for analysis in query_result:
    # Convert time_created to Boston timezone and format it
    time_created = analysis['time_created'].astimezone(boston_tz).strftime('%Y:%m:%d %H:%M')

    # Create a dictionary with modified time_created
    processed_row = {
        'aid': analysis['aid'],
        'analysis_name': analysis['analysis_name'],
        # 'analyst_name': analysis['analyst_name'],
        # 'analyst_id': analysis['analyst_id'],
        'time_created': time_created,  # modified time_created
        'details': analysis['details'],
        'owners_count': analysis['owners_count'],
        'status': analysis['status'],
    }
    
    processed_result.append(processed_row)
test_df = pd.DataFrame(processed_result)

analysis_history_component(test_df)
