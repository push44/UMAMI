import config
import json
import dash
import dash_bootstrap_components as dbc
import urllib.parse
import plotly.express as px
import numpy as np
import pandas as pd

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
        if len(add_filter_features)>0:
            col_index = {}
            for col in add_filter_features:
                col_index[col] = set(filtered_df[filtered_df[col].isnull()==False].index)

            cat1_index = set()
            for col in col_index:
                cat1_index.update(col_index[col])

            cat1_df = filtered_df.iloc[list(cat1_index)].copy(deep=True)

            cat3_index = set(filtered_df.index) - cat1_index
            cat3_df = filtered_df.iloc[list(cat3_index)].copy(deep=True)

        else:
            cat1_df = filtered_df
            cat3_df = pd.DataFrame(columns=filtered_df.columns)
        cat1_df["Category:"] = "Satisfies filter"
        cat3_df["Category:"] = "Filter status unknown"

        # Category 2: Does not satisfy filter, records where at least one filtred attributes is non-null and does not meet the corresponding filter conditions.
        cat2_df = dataframe.iloc[unsatisfied_indices].copy(deep=True)
        cat2_df["Category:"] = "Does not satisfies filter"

        # Category 3: Filter status unknown, records where all non-null attributes meet the corresponding filtered condition, and where at least one filtered attribute is null.

        #cat3_df = filtered_df[filtered_df.isnull().sum(axis=1)>0].copy(deep=True)
        #cat3_df["Category:"] = "Filter status unknown"

        fig = px.scatter(pd.concat([
            cat1_df, cat2_df, cat3_df
        ]), x=xaxis_column_name, y=yaxis_column_name, color="Category:")
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

        elm_in_div = len(div_children)

        if triggered_id == "add-filter":
            new_div_child = create_new_dropdown_div(elm_in_div, dataframe.columns[2:])
            div_children.append(new_div_child)

        elif triggered_id != "add-filter":
            for idx, val in enumerate(remove_clicks):
                if val is not None:
                    #print(f"All the remove buttons: {remove_clicks}")
                    #print(f"The index pertaining to the remove button clicked: {idx}")
                    #print(f"The number of time this particualr remove button was clicked: {val}")
                    del div_children[idx]

        return div_children

    #2.2) Update filter sliders on variable selection
    @app.callback(
        Output({"type":"filter-slider", "index": MATCH}, "min"),
        Output({"type":"filter-slider", "index": MATCH}, "max"),
        Output({"type":"filter-slider", "index": MATCH}, "value"),
        Output({"type":"filter-output-container", "index": MATCH}, "children"),
        Input({"type": "filter-dropdown", "index": MATCH}, "value"),
        Input({"type":"filter-slider", "index": MATCH}, "value"),
        State({"type":"filter-slider", "index": MATCH}, "min"),
        State({"type":"filter-slider", "index": MATCH}, "max"),
        State({"type":"filter-slider", "index": MATCH}, "value")
    )
    def update_filter_slider_on_variable_selection(column, filter_slider, default_min, default_max, default_value):
        ctx = dash.callback_context

        if ctx.triggered:
            ctx_triggered = ctx.triggered
            json_triggered = json.loads(ctx_triggered[0]["prop_id"].split(".value")[0])
            trigger_input_type = json_triggered["type"]

            if trigger_input_type=="filter-dropdown":
                if column == None:
                    min = -1000
                    max = 1000
                else:
                    min = dataframe[column].min()
                    max = dataframe[column].max()
                slider_value = [min, max]

            else:
                slider_value = filter_slider
                min, max = default_min, default_max

        else:
            min, max = default_min, default_max
            slider_value = default_value

        slider_value_display = list(map(lambda val: round(val, 3), slider_value))
        return min, max, slider_value, f"{slider_value_display}"

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
                        'backgroundColor': 'tomato',
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