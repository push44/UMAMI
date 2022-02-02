# Add feature 1 then feature 2 then remove feature 1 and add feature 3...then feature 3 fails to update as filter-dropdown is not triggered.
import config
import json
import dash
import dash_bootstrap_components as dbc
import urllib.parse
import plotly.express as px
import numpy as np
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn' Set to None because of False Positive warning for the current use case.

from dash.dependencies import Input
from dash.dependencies import Output
from dash.dependencies import State
from dash.dependencies import ALL, MATCH

from read import read
from layout import create_new_dropdown_div
from layout import create_layout
from layout import create_filter_table

def main(dataframe):

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
        State({"type": "filter-dropdown", "index": ALL}, "value")
    )
    def update_scatter_plot(xaxis_column_name, yaxis_column_name, filter_slider, filter_dropdown):

        add_filter_features = list(filter(lambda val: val!=None, filter_dropdown))
        selected_bounds = np.array(filter_slider).reshape(-1, 2)

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

    #2.1) Publish default filter on click event
    @app.callback(
        Output("dropdown-container", "children"),
        [Input("add-filter", "n_clicks"),
        Input({"type":"remove-filter", "index":ALL}, "n_clicks")],
        [State("dropdown-container", "children")],
        prevent_initial_call=True
    )
    def display_dropdown(add_clicks, remove_clicks, div_children):
        ctx = dash.callback_context
        triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]
        
        id_index = add_clicks

        if triggered_id == "add-filter":

            elm_in_div = len(div_children)
            dropdown_menue = dataframe.columns[2:]
            if elm_in_div>0:
                values = []
                for i in range(elm_in_div):
                    value = div_children[i]["props"]["children"][2]["props"]["value"]
                    values.append(value)
                dropdown_menue = [val for val in dropdown_menue if not val in values]

            new_div_child = create_new_dropdown_div(id_index, dropdown_menue)
            div_children.append(new_div_child)

        elif triggered_id != "add-filter":
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
        Input({"type": "filter-dropdown", "index": MATCH}, "value"),
        Input({"type":"filter-slider", "index": MATCH}, "value"),
        State({"type":"filter-slider", "index": MATCH}, "min"),
        State({"type":"filter-slider", "index": MATCH}, "max"),
        State({"type":"filter-slider", "index": MATCH}, "value"),
        prevent_initial_call=True
    )
    def update_filter_slider(column, filter_slider, default_min, default_max, default_value):
        ctx = dash.callback_context

        ctx_triggered = ctx.triggered
        json_triggered = json.loads(ctx_triggered[0]["prop_id"].split(".value")[0])
        trigger_input_type = json_triggered["type"]        

        if trigger_input_type=="filter-dropdown":
            min_val, max_val = dataframe[column].min(), dataframe[column].max()
            slider_value = [min_val, max_val]
        else:
            min_val, max_val = default_min, default_max
            slider_value = filter_slider

        is_int = all(val.is_integer() for val in dataframe[column].dropna(axis=0))
        step_val = 1 if is_int else 0.01

        if is_int:
            slider_value_display = list(map(int, slider_value))
            
        else:
            slider_value_display = list(map(lambda val: round(val, 2), slider_value))
        return min_val, max_val, slider_value, step_val, f"{slider_value_display}"

    ############################################
    ############## 3)Filter table ##############
    ############################################

    #Update table on click event
    @app.callback(
        Output("table-id", "data"),
        Output("table-id", "style_data_conditional"),
        Output("download-link", "href"),
        Input("add-filter", "n_clicks"),
        Input({"type": "filter-slider", "index": ALL}, "value"),
        State({"type": "filter-dropdown", "index": ALL}, "value")
    )
    def on_add_click(add_filter_n_clicks, filter_slider, filter_dropdown):

        add_filter_features = list(filter(lambda val: val!=None, filter_dropdown))
        selected_bounds = np.array(filter_slider).reshape(-1, 2)

        filtered_df, _ = create_filter_table(
            dataframe,
            add_filter_features,
            selected_bounds
        )

        csv_string = filtered_df.to_csv(index=False, encoding="utf-8")
        csv_string = "data:text/csv;charset=utf-8,%EF%BB%BF" + urllib.parse.quote(csv_string)
   
        #filtered_df = filtered_df.sample(frac=1)

        style_data_condition = [
                                {
                        'if': {
                            'filter_query': '{{{}}} is blank'.format(col)
                        },
                        'backgroundColor': "#00CC96",
                        'color': 'white'
                    } for col in add_filter_features
        ]

        return filtered_df.to_dict("records"), style_data_condition, csv_string

    app.run_server(debug=True)

if __name__ == "__main__":
    #external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
    external_stylesheets = [dbc.themes.COSMO, dbc.icons.BOOTSTRAP]
    app = dash.Dash("__main__", external_stylesheets=external_stylesheets)
    main(dataframe = read(config.SCHEMA_FILE, config.DATA_FILE))