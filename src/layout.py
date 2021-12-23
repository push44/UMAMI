from dash.dependencies import Output
import dash_table

import pandas as pd
import numpy as np
import dash_html_components as html
import dash_core_components as dcc

def thresholds(df, x, y, lb_x, ub_x, lb_y, ub_y):
    """Returns updated dataframe after thresholding for scatter plot"""

    ################## Zero non-None ##################
    if lb_x==None and ub_x==None and lb_y==None and ub_y==None:
        new_df = df

    ################## One non-None ##################
    elif lb_x!=None and ub_x==None and lb_y==None and ub_y==None:
        new_df = df[df[x]>=lb_x]

    elif lb_x==None and ub_x!=None and lb_y==None and ub_y==None:
        new_df = df[df[x]<=ub_x]

    elif lb_x==None and ub_x==None and lb_y!=None and ub_y==None:
        new_df = df[df[y]>=lb_y]

    elif lb_x==None and ub_x==None and lb_y==None and ub_y!=None:
        new_df = df[df[y]<=ub_y]

    ################## Two non-None ##################
    # lb_x = non-None
    elif lb_x!=None and ub_x!=None and lb_y==None and ub_y==None:
        new_df = df[(df[x]>=lb_x) & (df[x]<=ub_x)]

    elif lb_x!=None and ub_x==None and lb_y!=None and ub_y==None:
        new_df = df[(df[x]>=lb_x) & (df[y]>=lb_y)]

    elif lb_x!=None and ub_x==None and lb_y==None and ub_y!=None:
        new_df = df[(df[x]>=lb_x) & (df[y]<=ub_y)]

    # ub_x = non-None
    elif lb_x==None and ub_x!=None and lb_y!=None and ub_y==None:
        new_df = df[(df[x]<=ub_x) & (df[y]>=lb_y)]

    elif lb_x==None and ub_x!=None and lb_y==None and ub_y!=None:
        new_df = df[(df[x]<=ub_x) & (df[y]<=ub_y)]

    # lb_y = non-None
    elif lb_x==None and ub_x==None and lb_y!=None and ub_y!=None:
        new_df = df[(df[y]>=lb_y) & (df[y]<=ub_y)]

    ################## Three non-None ##################
    # lb_x = non-None
    elif lb_x!=None and ub_x!=None and lb_y!=None and ub_y==None:
        new_df = df[(df[x]>=lb_x) & (df[x]<=ub_x) & (df[y]>=lb_y)]

    elif lb_x!=None and ub_x!=None and lb_y==None and ub_y!=None:
        new_df = df[(df[x]>=lb_x) & (df[x]<=ub_x) & (df[y]<=ub_y)]

    elif lb_x!=None and ub_x==None and lb_y!=None and ub_y!=None:
        new_df = df[(df[x]>=lb_x) & (df[y]>=lb_y) & (df[y]<=ub_y)]

    # ub_x = non-None
    elif lb_x==None and ub_x!=None and lb_y!=None and ub_y!=None:
        new_df = df[(df[x]<=ub_x) & (df[y]>=lb_y) & (df[y]<=ub_y)]

    ################## Four(All) non-None ##################
    else:
        new_df = df[(df[x]>=lb_x) & (df[x]<=ub_x) & (df[y]>=lb_y) & (df[y]<=ub_y)]

    return new_df

def create_input(input_id, input_placeholder):
    # Return input object to receive bounds
    return dcc.Input(
                id=input_id,
                type="number",
                placeholder=input_placeholder,
                min=-np.inf,
                max=np.inf,
                style={"width":"30%"}
            )

#remove_features
def create_table_df(dataframe, clicks, add_features, bounds):
    """Returns pandas dataframe of feature names and number of out of bounds values"""
    # Copy dataframe to a new variable (To store changed/ or new dataframe)
    new_df = dataframe.copy(deep=True)

    # Drop features that are not required for out of range table
    dataframe = dataframe.drop(["case_name", "source"], axis=1)

    # Initialse a dataframe with zero out of range values (since no filter is selected)
    table_df = pd.DataFrame({
        "Features": dataframe.columns,
        "Out-of-range-values": [0]*len(dataframe.columns)
    })

    # Initialize a data dictionary to store out of range values per feature
    data = dict(zip(table_df["Features"].values, table_df["Out-of-range-values"].values))

    # Iterate over features to be added
    for ind, feat in enumerate(add_features):
        # Avoid if feature is also must be removed
        #if not feat in remove_features:
        lb, ub = bounds[ind]
        data[feat] = dataframe[(dataframe[feat]<lb) | (dataframe[feat]>ub)].shape[0]
        
        # new_df that meets the criterias
        if lb==None:
            new_df = new_df[new_df[feat]<ub]
        elif ub==None:
            new_df = new_df[new_df[feat]>lb]
        elif lb==None and ub==None:
            pass
        else:
            new_df = new_df[(new_df[feat]>lb) & (new_df[feat]<ub)]

        # Convert to dataframe
        table_df = pd.DataFrame({
            "Features": list(data.keys()),
            "Out-of-range-values": list(data.values())
        })

        # Sort the table according to out of range values
        #table_df.sort_values("Out-of-range-values", inplace=True, ascending=False)
        
    return table_df, new_df

def create_slider(slider_id, min_val, max_val):
    return dcc.RangeSlider(
            id = slider_id,
            min = min_val,
            max = max_val,
            step = 0.001,
            value = [min_val, max_val],
            updatemode = "drag"
    )

def create_dropdown_div(dropdown_id, features, column, slider_div):
    return html.Div(
            children=[
                        dcc.Dropdown(
                                    id=dropdown_id,
                                    options=[{'label': col, 'value': col} for col in features],
                                    value=column ,
                                    style={"width":"150px"},
                                    clearable=False          
                        ),
                        slider_div
                        
            ],
            style = {"display":"flex"}
        )

def create_new_dropdown_div(click_event, dropdown_list):
    """Returns dropdown object indexed according to click event (number of clicks)
    for adding new filter when one is selected"""

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


    """slider = create_slider(
        slider_id=f"slider-id",
        min_val = -10000,
        max_val = 10000
    )"""

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

    # Create new_dropdown for add filter
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


def create_layout(df):
    """
    Returns page layout
    """
    features = df.columns
    ################## Page Header ##################
    header_div = html.Div(
        children=[
            html.H1(
                children="Uncertainty Managed Access to Microstructures Interface Project",
                style={'textAlign': 'center'}
            ),
        ]
    )

    ################## Scatter Plot ##################

    # x axis
    xaxis_slider = create_slider(
        slider_id = "my-range-slider-x",
        min_val = df["ABS_wf_D"].min(),
        max_val = df["ABS_wf_D"].max()
    )

    slider_x_div = html.Div(
        children = [
            xaxis_slider,
            html.Div(f"{xaxis_slider.value}", id = "xaxis-output-container")
        ],
        style={"width":"150px"}
    )

    x_dropdown_div = create_dropdown_div(
        dropdown_id = "xaxis-column",
        features = features[2:],
        column = "ABS_wf_D",
        slider_div = slider_x_div
    )

    # y axis
    yaxis_slider = create_slider(
        slider_id = "my-range-slider-y",
        min_val = df["STAT_CC_D"].min(),
        max_val = df["STAT_CC_D"].max()
    )

    slider_y_div = html.Div(
        children = [
            yaxis_slider,
            html.Div(f"{yaxis_slider.value}", id = "yaxis-output-container")
        ],
        style={"width":"150px"}
    )

    y_dropdown_div = create_dropdown_div(
        dropdown_id = "yaxis-column",
        features = features[2:],
        column = "STAT_CC_D",
        slider_div = slider_y_div
    )

    # Dropdown div
    dropdown_div = html.Div(
        children=[
            x_dropdown_div,
            y_dropdown_div,
            
        ],
        style={"display":"grid"}
    )

    # Scatter plot object
    graph_object = dcc.Graph(id='indicator-graphic')

    # Scatter plot div with dropdowns
    scatter_plot_div = html.Div(
        children=[
            html.H2(
                children = "Scatter Plot"
            ),
            dropdown_div,
            graph_object
        ]
    )

    ################## Add/ Remove Filters ##################

    # Adding Filters
    add_filter_div = html.Div(
        children=[
            html.Button("Add Filter", id="add-filter", n_clicks=0),
            html.Div(id="dropdown-container", children=[])
        ]
    )

    # Removing Filters
    """remove_filter_div = html.Div(
        children=[
            html.Button("Remove Filter", id="remove-filter", n_clicks=0),
            html.Div(id="dropdown-container-remove", children=[])
        ]
    )"""

    # Adding/ Removing filter div
    #remove_filter_div
    filter_div = html.Div(
        children=[
            html.H2(
                children="Add Filters"
            ),
            add_filter_div,
        ]
    )

    ################## Table Object (Out of range table) ##################
    """table_object = dash_table.DataTable(
        id = "table-id",
        columns = [{"name": i, "id": i} for i in ["Features", "Out-of-range-values"]],
        style_table={
            "width":"30%",
        },
        style_cell = {
            "text_align": "left",
            "font_size": "14px"
        },
        style_header = {
            "text_align": "left",
            "font_size": "16px",
            "font_weight": "bold"
        }
    )"""
    
    # Out of range table div
    """table_div = html.Div(
            children=[
                html.H2(
                    children="Table"
                ),
                table_object      
            ]
        )"""

    ################## Table Object (Sample table after filter/s) ##################
    table_object = dash_table.DataTable(
        id="table-id",
        columns = [{"name": i, "id": i} for i in features],
        sort_action="native",
        sort_mode="multi",
        page_action="native",
        page_current=0,
        page_size=10,
    )

    # After filter sample table div
    table_div = html.Div(
        children=[
            html.H2(
                children="Sample Table"
            ),
            table_object
        ]
    )

    ################## Download Data Reference Link ##################
    reference_link_object = html.A(
        "Download Data",
        id = "download-link",
        download = "rawdata.csv",
        href = "",
        target = "_blank"
    )

    ################## Page Arrangement ##################

    # First half of page with filters and scatter plot
    top_half_div = html.Div(
        children= [
            scatter_plot_div,
            filter_div,
            html.Div(id="dummy-output")
        ]
    )

    # Bottom half of page with table and download link
    #table_div,
    bottom_half_div = html.Div(
        children= [ 
            table_div,
            reference_link_object
        ]
    )

    # Full page
    page_div = html.Div(
        children = [
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

