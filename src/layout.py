import dash_table
import dash_html_components as html
import dash_core_components as dcc

#################### Helper Functions ####################

#1) Filter table after add-filter
def create_filter_table(dataframe, add_features, bounds):
    """Returns filtered pandas dataframe"""
    new_df = dataframe.copy(deep=True)

    # Iterate over features to be added
    for ind, feat in enumerate(add_features):
        lb, ub = bounds[ind]
        new_df = new_df[(new_df[feat]>=lb) & (new_df[feat]<=ub)]
        
    return new_df

#2) Dropdown menue for scatter plot
def create_dropdown_div(dropdown_id, features, column):
    """Return dropdown menue"""
    return html.Div(
            children=[
                        dcc.Dropdown(
                                    id=dropdown_id,
                                    options=[{'label': col, 'value': col} for col in features],
                                    value=column ,
                                    style={"width":"150px"},
                                    clearable=False          
                        )
                        
            ],
            style = {"display":"flex"}
        )

#3) Dropdown to publish new dropdown to add new filter
def create_new_dropdown_div(click_event, dropdown_list):
    """Returns dropdown object indexed according to click event (number of clicks)
    for adding new filter when one is selected"""

    # Slider div indexed with n_clicks
    slider = dcc.RangeSlider(
        id = {
            "type": "filter-slider",
            "index": click_event
        },
        min = -1000,
        max = 1000,
        step = 0.001,
        value = [-1000, 1000],
        updatemode = "drag"
    )

    slider_div = html.Div(
        children = [
            slider,
            html.Div(f"{slider.value}", id={
                    "type": "filter-output-container",
                    "index": click_event
            })
        ],
        style={"width":"150px"}
    )

    # new dropdown object indexed with n_clicks
    new_dropdown = dcc.Dropdown(
            id={
                "type": "filter-dropdown",
                "index": click_event
            },
            options=[{"label":i, "value":i} for i in dropdown_list],
            style={"width":"60%"},
            clearable=False
        )

    return html.Div(
            [
                    html.Div(
                        [
                            new_dropdown,
                            slider_div
                        ],
                        style = {"display":"inline-flex"}
                )
            ],
            style={"display":"grid"}
        )

#################### Return actual page element functions ####################

#1) Page header
def return_header():
    return html.Div(
            children=[
                        html.H1(
                            children="Uncertainty Managed Access to Microstructures Interface Project",
                            style={'textAlign': 'center'}
            
                        )
            ]
    )

#2) Scatter plot
def return_scatter_plot_div(features):

    # x dropdown div
    x_dropdown_div = create_dropdown_div(
        dropdown_id = "xaxis-column",
        features = features,
        column = "ABS_wf_D"
    )

    # y dropdown div
    y_dropdown_div = create_dropdown_div(
        dropdown_id = "yaxis-column",
        features = features,
        column = "STAT_CC_D"
    )

    # Dropdown div
    dropdown_div = html.Div(
        children=[
            x_dropdown_div,
            y_dropdown_div
        ],
        style={"display":"grid"}
    )

    # Scatter plot object
    graph_object = dcc.Graph(id='indicator-graphic')

    return html.Div(
            children=[
                html.H2(
                    children = "Scatter Plot"
                ),
                dropdown_div,
                graph_object
            ]
    )

#3) Filter div
def return_filter_div():
    add_filter_div = html.Div(
        children=[
            html.Button("Add New Filter", id="add-filter", n_clicks=0),
            html.Div(id="dropdown-container", children=[])
        ]
    )

    return html.Div(
            children=[
                html.H2(
                    children="Add Filters"
                ),
                add_filter_div,
            ]
    )

#4) Table after filters
def return_filter_table(features):
    table_object = dash_table.DataTable(
        id="table-id",
        columns = [{"name": i, "id": i} for i in features],
        sort_action="native",
        sort_mode="multi",
        page_action="native",
        page_current=0,
        page_size=10,
    )

    return html.Div(
        children=[
            html.H2(
                children="Sample Table"
            ),
            table_object
        ]
    )

#5) Table download link
def return_download_link():
    return html.A(
        "Download Data",
        id = "download-link",
        download = "rawdata.csv",
        href = "",
        target = "_blank"
    )

#6) Top half of page
def return_divs(div1, div2):
    return html.Div(
        children= [
            div1,
            div2
        ]
    )
####################### Page layout #######################

def create_layout(df):
    """
    Returns page layout
    """
    features = df.columns

    #######################################################
    ################## Get page elements ##################
    #######################################################

    #1) Page Header
    header_div = return_header()
    #2) Scatter Plot
    scatter_plot_div = return_scatter_plot_div(features[2:])
    #3) Add Filters
    filter_div = return_filter_div()
    #4) Table after filters
    table_div = return_filter_table(features)
    #5) Download Data Reference Link
    download_link_object = return_download_link()

    ######################################################
    ################## Page Arrangement ##################
    ######################################################

    #6) Top half of page
    top_half_div = return_divs(
        scatter_plot_div,
        filter_div
    )

    #7) Bottom half of page
    bottom_half_div = return_divs(
        table_div,
        download_link_object
    )

    #8) Full page
    page_div = return_divs(
        top_half_div,
        bottom_half_div,
    )

    # Final arrangement
    return html.Div(
        children=[
            header_div,
            page_div
        ]
    )