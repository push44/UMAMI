import dash_table

import pandas as pd
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
    """Return input object to receive bounds"""
    return dcc.Input(
                id=input_id,
                type="number",
                placeholder=input_placeholder,
                min=-1001,
                max=1001,
                style={"width":"30%"}
            )

def create_dropdown_div(input_id, default_value, lb, ub, dropdown_list):
    """Return Div object with dropdown menue along with the options of receiving lower bound
    and upper bound for adding filter"""
    return html.Div(
            children=[
                        dcc.Dropdown(
                                    id=input_id,
                                    options=[{'label': col, 'value': col} for col in dropdown_list],
                                    value=default_value ,
                                    style={"width":"60%"}                       
                        ),
                        lb,
                        ub,            
            ],
            style = {"display":"inline-flex"}
        )

def create_new_dropdown_div(click_event, dropdown_list):
    """Returns dropdown object indexed according to click event (number of clicks)
    for adding new filter when one is selected"""
    new_dropdown = dcc.Dropdown(
            id={
                "type": "filter-dropdown",
                "index": click_event
            },
            options=[{"label":i, "value":i} for i in dropdown_list],
            style={"width":"60%"}
        )

    new_lb = create_input({"type":"number", "index": click_event}, "Lower Bound")
    new_ub = create_input({"type":"number", "index": click_event}, "Upper Bound")

    return html.Div(
            [
                    html.Div(
                        [
                            new_dropdown,
                            new_lb,
                            new_ub
                        ],
                        style = {"display":"inline-flex"}
                )
            ],
            style={"display":"grid"}
        )

def create_table_df(dataframe, clicks, features, bounds):
    """Returns pandas dataframe of feature names and number of out of bounds values"""
    dataframe = dataframe.drop(["case_name", "source"], axis=1)
    table_df = pd.DataFrame({
        "Features": dataframe.columns,
        "Out-of-range-values": [0]*len(dataframe.columns)
    })
    if clicks>0:
        data = dict(zip(table_df["Features"].values, table_df["Out-of-range-values"].values))
        for ind, feat in enumerate(features):
            lb, ub = bounds[ind]
            data[feat] = dataframe[(dataframe[feat]<lb) | (dataframe[feat]>ub)].shape[0]

        table_df = pd.DataFrame({
            "Features": list(data.keys()),
            "Out-of-range-values": list(data.values())
        })

    table_df.sort_values("Out-of-range-values", inplace=True, ascending=False)
    return table_df

def create_layout(features):
    """
    Returns page layout
    """

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
    lb_x = create_input("lbx", "Lower Bound")
    lb_y = create_input("lby", "Lower Bound")
    ub_x = create_input("ubx", "Upper Bound")
    ub_y = create_input("uby", "Upper Bound")

    x_dropdown_div = create_dropdown_div("xaxis-column","ABS_wf_D", lb_x, ub_x, features[2:])
    y_dropdown_div = create_dropdown_div("yaxis-column", "STAT_CC_D", lb_y, ub_y, features[2:])

    dropdown_div = html.Div(
        children=[
            x_dropdown_div,
            y_dropdown_div
        ],
        style={"display":"grid"}
    )

    graph_object = dcc.Graph(id='indicator-graphic')

    scatter_plot_div = html.Div(
        children=[
            html.H2(
                children = "Scatter Plot"
            ),
            dropdown_div,
            graph_object
        ]
    )

    ################## Adding Filters ##################
    filter_div = html.Div(
        children=[
            html.H2(
                children="Filters"
            ),
            html.P(
                children="To remove filter click add filter with bounds -1000 and 1000."
            ),
            html.Button("Add Filter", id="add-filter", n_clicks=0),
            html.Div(id="dropdown-container", children=[]),
            html.Div(id="empty-output")
        ]
    )
    ################## Table Object ##################
    table_object = dash_table.DataTable(
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
    )
    
    table_div = html.Div(
            children=[
                html.H2(
                    children="Table"
                ),
                table_object      
            ]
        )

    return html.Div(
        children=[
            header_div,
            scatter_plot_div,
            filter_div,
            table_div
        ]
    )
