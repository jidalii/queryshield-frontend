from st_aggrid import AgGrid, GridOptionsBuilder, JsCode, GridUpdateMode

def analysis_history_component(df):
    # Build Grid Options for Ag-Grid
    gd = GridOptionsBuilder.from_dataframe(df)
    # gd.configure_pagination(enabled=True)
    gd.configure_selection(selection_mode="single")
    
    gd.configure_column("aid", header_name="Analysis ID")
    gd.configure_column("analysis_name", header_name="Analysis Name")
    gd.configure_column("time_created", header_name="Time Created")
    gd.configure_column("owners_count", header_name="Owners Registered")
    

    # Configure Action column with a URL renderer
    gd.configure_column(
        "status",
        headerName="Status",
        cellRenderer=JsCode(
            """
            class UrlCellRenderer {
            init(params) {
                this.eGui = document.createElement('a');
                this.eGui.innerText = params.data["status"];
                this.eGui.setAttribute('href', '/Analysis_History?aid=' + params.data["Analysis ID"]);
                this.eGui.setAttribute('style', "text-decoration:none");
                this.eGui.setAttribute('target', "_blank");
            }
            getGui() {
                return this.eGui;
            }
            }
            """
        ),
    )
    gd.configure_column(
        "details",
        headerName="Analysis Description",
        cellRenderer=JsCode(
            """
            class UrlCellRenderer {
            init(params) {
                this.eGui = document.createElement('a');
                this.eGui.innerText = "View Details";
                this.eGui.setAttribute('href', '/Analysis_Detail?aid=' + params.data["aid"]);
                this.eGui.setAttribute('style', "text-decoration:none");
                this.eGui.setAttribute('target', "_blank");
            }
            getGui() {
                return this.eGui;
            }
            }
            """
        ),
    )

    gridoptions = gd.build()

    # Display the DataFrame in AgGrid within col1
    grid_table = AgGrid(
        df,
        gridOptions=gridoptions,
        allow_unsafe_jscode=True,
        height=500,
        theme="streamlit",
        update_mode=GridUpdateMode.SELECTION_CHANGED,
    )