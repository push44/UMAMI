import config
import json
import dash
import dash_bootstrap_components as dbc
import urllib.parse
import plotly.express as px
import numpy as np
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn' Set to None because of False Positive warning for the current use case.

from math import ceil, floor
from dash.dependencies import Input
from dash.dependencies import Output
from dash.dependencies import State
from dash.dependencies import ALL, MATCH
from dash import dcc

from read import read
from layout import create_new_dropdown_div
from layout import create_layout
from layout import create_filter_table

def callback_func(dataframe):

    # Drop rows having all attributes: null
    dataframe.dropna(axis=0, how="all", inplace=True)

    # Get app layout
    app.layout = create_layout(dataframe)

    ############################################
    ############## 1)Scatter Plot ##############
    ############################################

    #Update scatter plot
    @app.callback(
        Output("indicator-graphic", "figure"),

        Input("xaxis-column", "value"),
        Input("yaxis-column", "value"),
        Input({"type": "filter-slider", "index": ALL}, "value"),

        State({"type": "filter-dropdown", "index": ALL}, "value"),
    )
    def update_scatter_plot(xaxis_column_name, yaxis_column_name, filter_slider, filter_dropdown):

        # List all selected features
        add_filter_features = list(filter(lambda val: val!=None, filter_dropdown))
        # List all choosen filter bounds
        selected_bounds = np.array(filter_slider).reshape(-1, 2)

        # get filter dataframe and indices of unsatisfied data points
        filtered_df, unsatisfied_indices = create_filter_table(
            dataframe,
            add_filter_features,
            selected_bounds
        )

        # Category 1: Satisfies filter, records where all filtered attributes are non-null and meet the filter conditions.
        # Category 3: Filter status unknown, records where all non-null attributes meet the corresponding filtered condition, and where at least one filtered attribute is null.

        temp_df = filtered_df.copy(deep=True)
        temp_df["cat"] = temp_df[add_filter_features].isnull().any(axis=1) # check any of the selected features has null value.

        cat1_df = temp_df[temp_df["cat"] != True]
        cat3_df = temp_df[temp_df["cat"] == True]
        
        cat1_df["Category:"] = "Satisfies filter"
        cat3_df["Category:"] = "Filter status unknown"

        # Category 2: Does not satisfy filter, records where at least one filtred attributes is non-null and does not meet the corresponding filter conditions.
        cat2_df = dataframe.iloc[unsatisfied_indices].copy(deep=True)
        cat2_df["Category:"] = "Does not satisfies filter"

        fig = px.scatter(pd.concat([cat1_df,cat2_df,cat3_df]),
                        x=xaxis_column_name,
                        y=yaxis_column_name,
                        color_discrete_map={
                            "Satisfies filter": "#636EFA",
                            "Filter status unknown": "#00CC96",
                            "Does not satisfies filter":"#EF553B"
                        },
                        color="Category:"
                    )
        return fig

    ############################################
    ################# 2)Filter #################
    ############################################

    #2.1) Publish default filter on add click event and remove filter on remove click event
    @app.callback(
        Output("dropdown-container", "children"),

        [Input("add-filter", "n_clicks"),
        Input({"type":"remove-filter", "index":ALL}, "n_clicks")],

        [State("dropdown-container", "children")],
        prevent_initial_call=True
    )
    def display_dropdown(add_clicks, remove_clicks, div_children):
        ctx = dash.callback_context # determining which input has fired (https://dash.plotly.com/advanced-callbacks)

        # extract fired input name
        triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]

        if triggered_id == "add-filter":
            # publish new dropdown
            elm_in_div = len(div_children)
            dropdown_menue = dataframe.columns[2:]
            if elm_in_div>0:
                values = []
                for i in range(elm_in_div):
                    value = div_children[i]["props"]["children"][2]["props"]["value"]
                    values.append(value)

                # dropdown menue do not contain features that are previously selected
                dropdown_menue = [val for val in dropdown_menue if not val in values]

            # add new dropdown
            new_div_child = create_new_dropdown_div(add_clicks, dropdown_menue)
            div_children.append(new_div_child)

        elif triggered_id != "add-filter":
            # remove filter
            for idx, val in enumerate(remove_clicks):
                if val is not None:
                    #print(f"All the remove buttons: {remove_clicks}")
                    #print(f"The index pertaining to the remove button clicked: {idx}")
                    #print(f"The number of time this particualr remove button was clicked: {val}")
                    del div_children[idx]

        return div_children

    #2.2) Update filter sliders
    @app.callback(
        Output({"type":"filter-slider", "index": MATCH}, "min"),
        Output({"type":"filter-slider", "index": MATCH}, "max"),
        Output({"type":"filter-slider", "index": MATCH}, "value"),
        Output({"type":"filter-slider", "index": MATCH}, "step"),
        Output({"type":"filter-output-container", "index": MATCH}, "children"),

        Input({"type":"filter-dropdown", "index": MATCH}, "value"),
        Input({"type":"filter-slider", "index": MATCH}, "value"),

        State({"type":"filter-slider", "index": MATCH}, "min"),
        State({"type":"filter-slider", "index": MATCH}, "max"),
        State({"type":"filter-slider", "index": MATCH}, "value"),
        prevent_initial_call=True
    )
    def update_filter_slider(column, filter_slider, default_min, default_max, default_value):
        ctx = dash.callback_context # determining which input has fired (https://dash.plotly.com/advanced-callbacks)

        # extract fired input name
        ctx_triggered = ctx.triggered
        json_triggered = json.loads(ctx_triggered[0]["prop_id"].split(".value")[0])
        trigger_input_type = json_triggered["type"]        

        if trigger_input_type=="filter-dropdown":
            # if new feature is selected then publish minimum and maximum bounds
            min_val, max_val = dataframe[column].min(), dataframe[column].max()
            slider_value = [min_val, max_val]

        else:
            # if feature is already selected then keep bounds unchanged
            min_val, max_val = default_min, default_max
            # change slider values
            slider_value = filter_slider

        is_int = all(val.is_integer() for val in dataframe[column].dropna(axis=0))

        if is_int:
            # if selected feature is integer type then update slider step value
            step_val = 1
            # display integer values
            slider_value_display = list(map(int, slider_value))

        if not is_int:
            step_val = 0.000001 # selected values from trial and error to overcome rounding issues
            slider_value[-1] = ceil(slider_value[-1] * 100000) / 100000 #round up to 5 decimal places
            slider_value[0] = floor(slider_value[0] * 100000) / 100000 #round down to 5 decimal places
            slider_value_display = slider_value

        return min_val, max_val, slider_value, step_val, f"{slider_value_display}"

    ############################################
    ############## 3)Filter table ##############
    ############################################

    #Update table on click event/ slider change
    @app.callback(
        Output("table-id", "data"),
        Output("table-id", "style_data_conditional"),

        Input("add-filter", "n_clicks"),
        Input({"type": "filter-slider", "index": ALL}, "value"),

        State({"type": "filter-dropdown", "index": ALL}, "value"),
        prevent_initial_call=True
    )
    def apply_filter(add_filter_n_clicks, filter_slider, filter_dropdown):

        add_filter_features = list(filter(lambda val: val!=None, filter_dropdown))
        selected_bounds = np.array(filter_slider).reshape(-1, 2)

        # received filtered dataframe
        filtered_df, _ = create_filter_table(
            dataframe,
            add_filter_features,
            selected_bounds
        )

        # update style data condition for sample display table (rows containing missing values in the selected features are highlighted in the sample display table)
        style_data_condition = [
                                {
                        'if': {
                            'filter_query': '{{{}}} is blank'.format(col)
                        },
                        'backgroundColor': "#00CC96",
                        'color': 'white'
                    } for col in add_filter_features
        ]

        return filtered_df.to_dict("records"), style_data_condition

    #############################################
    ############# 4)Download button #############
    #############################################

    @app.callback(
        Output("download-dataframe-csv", "data"),

        Input("btn_csv", "n_clicks"),

        State("table-id", "data"),
        prevent_initial_call=True,
    )
    def download_button(n_clicks, data):
        return dcc.send_data_frame(pd.DataFrame(data).to_csv, "data.csv")

    # Change debug mode
    app.run_server(debug=True)

if __name__ == "__main__":
    #external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
    external_stylesheets = [dbc.themes.COSMO, dbc.icons.BOOTSTRAP]

    app = dash.Dash("__main__", external_stylesheets=external_stylesheets)

    callback_func(dataframe = read(config.SCHEMA_FILE, config.DATA_FILE))