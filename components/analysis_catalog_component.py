import streamlit as st
import pandas as pd
import numpy as np
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode


def analysis_catalog_component(df):
    gd = GridOptionsBuilder.from_dataframe(df)
    gd.configure_column("aid", header_name="Analysis ID")
    gd.configure_column("analysis_name", header_name="Analysis Name")
    gd.configure_column("analyst_name", header_name="Analyst Name")
    gd.configure_column("analyst_id", header_name="Analyst ID")
    gd.configure_column("time_created", header_name="Time Created")
    gd.configure_column("owners_count", header_name="Owners Registered")

    # Example for configuring a column with a custom cell renderer
    gd.configure_column(
        "details",
        headerName="Analysis Description",
        cellRenderer=JsCode(
            """
            class UrlCellRenderer {
            init(params) {
                this.eGui = document.createElement('a');
                this.eGui.innerText = "View Details";
                this.eGui.setAttribute('href', '/Analysis_Detail_View?aid=' + params.data["aid"]);
                console.log(params);
                this.eGui.setAttribute('style', "text-decoration:none");
                this.eGui.setAttribute('target', "_blank");
            }
            getGui() {
                return this.eGui;
            }
            }
            """
        ),
        width=300,
    )

    gd.configure_column(
        "Action",
        headerName="Action",
        cellRenderer=JsCode(
            """
            class UrlCellRenderer {
            init(params) {
                this.eGui = document.createElement('a');
                this.eGui.innerText = "Share Data";
                this.eGui.setAttribute('href', '/Share_Data?aid=' + params.data["aid"] + '&uid=' + params.data["analyst_id"]);
                console.log(params);
                this.eGui.setAttribute('style', "text-decoration:none");
                this.eGui.setAttribute('target', "_blank");
            }
            getGui() {
                return this.eGui;
            }
            }
            """
        ),
        width=300,
    )

    # Build the grid options
    gridoptions = gd.build()

    # Display the DataFrame in AgGrid
    AgGrid(
        df,
        gridOptions=gridoptions,
        allow_unsafe_jscode=True,
        height=500,
        # theme="alpine",
    )