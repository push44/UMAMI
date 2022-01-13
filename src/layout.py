#import dash_table
from dash import dash_table, html, dcc
from dash.dependencies import Output
#import dash_html_components as html
#import dash_core_components as dcc
import dash_bootstrap_components as dbc

#################### Helper Functions ####################

#1) Filter table after add-filter
def create_filter_table(dataframe, add_features, bounds):
    """Returns filtered pandas dataframe"""
    #dataframe = dataframe.fillna('N/A').replace('', 'N/A')
    unsatisfied_indices = set()
    # Iterate over features to be added
    for ind, feat in enumerate(add_features):
        lb, ub = bounds[ind]
        #print(lb, ub, dataframe[feat].min(), dataframe[feat].max())
        unsatisfied_indices.update(
            set(dataframe[(dataframe[feat]<lb) | (dataframe[feat]>ub)].index.tolist())
        )
    
    new_df = dataframe.iloc[list(
        set(dataframe.index) - unsatisfied_indices
    )]
    #print(len(unsatisfied_indices))
    return new_df, list(unsatisfied_indices)

#2) Dropdown menue for scatter plot
def create_dropdown_div(dropdown_id, features, column, display_name, right_margin="0px"):
    """Return dropdown menue"""
    return html.Div(
            children=[
                        html.H5(
                            children=[display_name],
                            style={"margin-right":"15px"}
                        ),
                        dcc.Dropdown(
                                    id=dropdown_id,
                                    options=[{'label': col, 'value': col} for col in features],
                                    value=column ,
                                    style={"width":"150px"},
                                    clearable=False          
                        )
                        
            ],
            style = {"display":"flex", "margin-right":right_margin}
        )

def make_tooltip(text, tooltip_target, placement="top"):
    return dbc.Tooltip(
        text,
        target=tooltip_target,
        placement=placement,
    )

#3) Dropdown to publish new dropdown to add new filter
def create_new_dropdown_div(elem_in_div, dropdown_list):
    """Returns dropdown object indexed according to click event (number of clicks)
    for adding new filter when one is selected"""
    # Remove filter button
    button_id = {"type": "remove-filter","index": elem_in_div}
    remove_button = html.I(
                        className="bi bi-dash-circle-fill",
                        id = button_id,
                        style={
                            "margin-right":"10px"
                        }
                    )

    # Tooltip for remove button
    remove_button_tooltip = make_tooltip("Remove Filter", button_id)

    # Slider div indexed with n_clicks
    slider = dcc.RangeSlider(
        id = {
            "type": "filter-slider",
            "index": elem_in_div
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
                    "index": elem_in_div
            })
        ],
        style={"width":"180px"}
    )

    # new dropdown object indexed with n_clicks
    new_dropdown = dcc.Dropdown(
            id={
                "type": "filter-dropdown",
                "index": elem_in_div
            },
            options=[{"label":i, "value":i} for i in dropdown_list],
            style={"width":"175px"},
            clearable=False
        )

    return html.Div(
            [
                    remove_button,
                    remove_button_tooltip,
                    new_dropdown,
                    slider_div
            ],
            style={"display":"inline-flex", "margin-top":"10px"}
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
        column = "ABS_wf_D",
        display_name="X-axis:",
        right_margin="40px"
    )

    # y dropdown div
    y_dropdown_div = create_dropdown_div(
        dropdown_id = "yaxis-column",
        features = features,
        column = "STAT_CC_D",
        display_name="Y-axis:"
    )

    # Dropdown div
    dropdown_div = html.Div(
        children=[
            x_dropdown_div,
            y_dropdown_div
        ],
        style={"display":"inline-flex", "margin-left":"80px"}
    )

    # Scatter plot object
    graph_object = html.Div(
        children=[dcc.Graph(id='indicator-graphic')]
    )

    return html.Div(
            children=[
                html.H2(
                    children = "Scatter Plot",
                    style={"text-align":"center"}
                ),
                dropdown_div,
                graph_object
            ],
            style={"width":"800px", "align-content":"center", "border":"2px black solid"}
    )

#3) Filter div
def return_filter_div():
    button_id = "add-filter"
    add_filter_div = html.Div(
        children=[
                html.Div(
                    children=[
                        html.Div(id="dropdown-container", children=[])
                    ]
                ),
                html.Div(
                    children=[
                        html.I(
                            id=button_id,
                            className="bi bi-plus-circle-fill",
                            n_clicks=0
                        )
                    ]
                )
            ],
            style={"margin-left":"20px"}
        )

    # Tooltip for add button
    add_button_tooltip = make_tooltip("Add New Filter", button_id)

    return html.Div(
            children=[
                html.H2(
                    children="Add Filters",
                    style={"text-align":"center"}
                ),
                add_filter_div,
                add_button_tooltip
            ],
            style={"width":"500px", "overflow":"scroll", "border":"2px black solid"}
    )

#4) Table after filters
def return_filter_table(features):
    table_object = html.Div(
        children=[
            dash_table.DataTable(
                id="table-id",
                columns = [{"name": i, "id": i} for i in features],
                style_data_conditional=[],
                sort_action="native",
                sort_mode="multi",
                page_action="native",
                page_current=0,
                page_size=10,
            )
        ],
        style={"overflow":"scroll", "margin-left":"50px", "border":"2px black solid"}
    )

    return html.Div(
        children=[
            html.H2(
                children="Sample Table",
                style={"text-align":"center"}
            ),
            table_object
        ],
        style={"width":"1200px"}
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
def return_top_half_divs(div1, div2):
    return html.Div(
        children= [
            div1,
            div2
        ],
        style={"display":"inline-flex", "height":"580px", "width":"1300px"}
    )

#7) Bottom half of page
def return_bottom_half_divs(div1, div2):
    return html.Div(
        children= [
            div1,
            div2
        ],
        style={"height":"500px", "width":"1300px", "margin-top":"50px"}
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
    top_half_div = return_top_half_divs(
        filter_div,
        scatter_plot_div
    )

    #7) Bottom half of page
    bottom_half_div = return_bottom_half_divs(
        table_div,
        download_link_object
    )

    #8) Full page
    page_div = html.Div(
        children=[
            top_half_div,
            bottom_half_div,
        ]
    )

    # Final arrangement
    return html.Div(
        children=[
            header_div,
            page_div
        ]
    )