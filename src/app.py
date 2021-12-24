import config
import json
import dash
import urllib.parse
import plotly.express as px
import numpy as np

from dash.dependencies import Input
from dash.dependencies import Output
from dash.dependencies import State
from dash.dependencies import ALL, MATCH

from read import read
from layout import create_new_dropdown_div
from layout import create_layout
from layout import create_filter_table

def main(dataframe):
    # Get app layout
    app.layout = create_layout(dataframe)

    ############################################
    ############## 1)Scatter Plot ##############
    ############################################

    #Update scatter plot
    @app.callback(
        Output("indicator-graphic", "figure"),
        Input("xaxis-column", "value"),
        Input("yaxis-column", "value")
    )
    def update_scatter_plot(xaxis_column_name, yaxis_column_name):
        fig = px.scatter(dataframe, x=xaxis_column_name, y=yaxis_column_name)
        return fig

    ############################################
    ################# 2)Filter #################
    ############################################

    #2.1) Publish default filter on click event
    @app.callback(
        Output("dropdown-container", "children"),
        Input("add-filter", "n_clicks"),
        State("dropdown-container", "children")
    )
    def display_dropdown(button_click, dropdown_children_state):
        new_dropdown_div = create_new_dropdown_div(button_click, dataframe.columns[2:])
        dropdown_children_state.append(new_dropdown_div)
        return dropdown_children_state

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
        return min, max, slider_value, f"{slider_value}"

    ############################################
    ############## 3)Filter table ##############
    ############################################

    #Update table on click event
    @app.callback(
        Output("table-id", "data"),
        Output("download-link", "href"),
        Input("add-filter", "n_clicks"),
        Input({"type": "filter-slider", "index": ALL}, "value"),
        State({"type": "filter-dropdown", "index": ALL}, "value")
    )
    def on_add_click(add_filter_n_clicks, filter_slider, filter_dropdown):

        add_filter_features = list(filter(lambda val: val!=None, filter_dropdown))
        selected_bounds = np.array(filter_slider).reshape(-1, 2)

        new_df = create_filter_table(
            dataframe,
            add_filter_features,
            selected_bounds
        )

        csv_string = new_df.to_csv(index=False, encoding="utf-8")
        csv_string = "data:text/csv;charset=utf-8,%EF%BB%BF" + urllib.parse.quote(csv_string)
   
        new_df.to_dict("records"), csv_string
        return new_df.to_dict("records"), csv_string

    app.run_server(debug=True)

if __name__ == "__main__":
    external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
    app = dash.Dash("__main__", external_stylesheets=external_stylesheets)
    main(dataframe = read(config.SCHEMA_FILE, config.DATA_FILE))