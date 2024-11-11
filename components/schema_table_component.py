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


def schema_table_component(schema, schema_types, category_df):
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
