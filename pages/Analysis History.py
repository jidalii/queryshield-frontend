# import streamlit as st
# import pandas as pd
# from sqlalchemy import create_engine
# import pytz

# from components.analysis_history_component import analysis_history_component
# from utils.db.db_services import fetch_analyst_analysis_history
# from components.sidebar_component import sidebar_login_component

# st.set_page_config("QueryShield", layout="wide")

# st.title("Analysis History")
# st.sidebar.title("QueryShield")

# engine = create_engine(
#     "postgresql+psycopg2://user1:12345678!@localhost:5432/queryshield"
# )
# if "logined" not in st.session_state:
#     st.session_state["logined"] = False

# sidebar_login_component(engine)

# # def history_table():
# sample_data = {
#     "Analysis ID": ["1012323", "103431346", "1134134173"],
#     "Analysis Name": ["Query1", "Query2", "Query3"],
#     "Analyst Name": ["Alice", "Alice", "Alice"],
#     "Analyst ID": ["101", "101", "101"],
#     "Time Created": ["2024-10-12 08:30", "2024-10-12 09:00", "2024-10-12 10:30"],
#     "Analysis Description": [
#         {"parameter_1": "value_1", "parameter_2": 100},
#         {"parameter_1": "value_2", "parameter_2": 200},
#         {"parameter_1": "value_3", "parameter_2": 300},
#     ],
#     "Owners Registered": [10, 20, 30],
#     "Status": ["Created", "Ready", "Failed"],
# }

# projectlist = [["project1", "project2"], [1,2]]

# query_result = fetch_analyst_analysis_history(engine, 1)

# boston_tz = pytz.timezone('America/New_York')
# processed_result = []
# for analysis in query_result:
#     # Convert time_created to Boston timezone and format it
#     time_created = analysis['time_created'].astimezone(boston_tz).strftime('%Y:%m:%d %H:%M')

#     # Create a dictionary with modified time_created
#     processed_row = {
#         'aid': analysis['aid'],
#         'analysis_name': analysis['analysis_name'],
#         # 'analyst_name': analysis['analyst_name'],
#         # 'analyst_id': analysis['analyst_id'],
#         'time_created': time_created,  # modified time_created
#         'details': analysis['details'],
#         'owners_count': analysis['owners_count'],
#         'status': analysis['status'],
#     }
    
#     processed_result.append(processed_row)
# test_df = pd.DataFrame(processed_result)
# # test_df = pd.DataFrame(projectlist, columns=["Projects", 'num'])

# analysis_history_component(test_df)
