import config
import json
import dash
import urllib.parse
import plotly.express as px
import numpy as np

from dash.dependencies import Input
from dash.dependencies import Output
from dash.dependencies import State
from dash.dependencies import ALL, MATCH, ALLSMALLER

from read import read
from layout import create_new_dropdown_div
from layout import create_layout
from layout import create_table_df
from layout import thresholds

def main(dataframe):
    # Get app layout
    app.layout = create_layout(dataframe)

    ############## Update scatter plot sliders on variable selection ##############
    # x axis
    @app.callback(
        Output("my-range-slider-x", "min"),
        Output("my-range-slider-x", "max"),
        Output("my-range-slider-x", "value"),
        Input("xaxis-column", "value")
    )
    def update_xaxis_values(xaxis_column):
        return [dataframe[xaxis_column].min(), dataframe[xaxis_column].max(), [dataframe[xaxis_column].min(), dataframe[xaxis_column].max()]]

    # y axis
    @app.callback(
        Output("my-range-slider-y", "min"),
        Output("my-range-slider-y", "max"),
        Output("my-range-slider-y", "value"),
        Input("yaxis-column", "value")
    )
    def update_yaxis_values(yaxis_column):
        return [dataframe[yaxis_column].min(), dataframe[yaxis_column].max(), [dataframe[yaxis_column].min(), dataframe[yaxis_column].max()]]

    ############## Update scatter plot on slider change ##############
    @app.callback(
        Output("indicator-graphic", "figure"),
        Output("xaxis-output-container", "children"),
        Output("yaxis-output-container", "children"),
        Input("my-range-slider-x", "value"),
        Input("my-range-slider-y", "value"),
        State("xaxis-column", "value"),
        State("yaxis-column", "value")
    )
    def update_scatter_plot(xaxis_values, yaxis_values, xaxis_column_name, yaxis_column_name):

        upadted_dataframe = thresholds(
            df = dataframe,
            x = xaxis_column_name,
            y = yaxis_column_name,
            lb_x = xaxis_values[0],
            ub_x = xaxis_values[1],
            lb_y = yaxis_values[0],
            ub_y = yaxis_values[1]
        )

        # Create scatter plot
        fig = px.scatter(upadted_dataframe, x=xaxis_column_name, y=yaxis_column_name)
        return fig, f"{xaxis_values}", f"{yaxis_values}"

    ############# Publish default filter on click event #############
    @app.callback(
        Output("dropdown-container", "children"),
        Input("add-filter", "n_clicks"),
        State("dropdown-container", "children")
    )
    def display_dropdown(button_click, dropdown_children_state):
        new_dropdown_div = create_new_dropdown_div(button_click, dataframe.columns[2:])
        dropdown_children_state.append(new_dropdown_div)

        return dropdown_children_state

    ########### Update filter sliders on variable selection ###########
    @app.callback(
        Output({"type":"filter-slider", "index": MATCH}, "min"),
        Output({"type":"filter-slider", "index": MATCH}, "max"),
        Input({"type": "filter-dropdown", "index": MATCH}, "value")
    )
    def update_filter_slider_on_variable_selection(column):
        if column == None:
            min = -1000
            max = 1000
        else:
            min = dataframe[column].min()
            max = dataframe[column].max()
        return min, max

    ####### Update filter slider output on slider change #######
    @app.callback(
        Output({"type":"filter-output-container", "index": MATCH}, "children"),
        Output({"type":"filter-slider", "index": MATCH}, "value"),
        Input({"type":"filter-slider", "index": MATCH}, "value")
    )
    def update_filter_slider_output_on_slider_change(filter_slider):
        return f"{filter_slider}", filter_slider

    ########### Update table on click event ###########
    @app.callback(
        Output("table-id", "data"),
        Output("download-link", "href"),
        Input("add-filter", "n_clicks"),
        Input({"type": "filter-slider", "index": ALL}, "value"),
        State({"type": "filter-dropdown", "index": ALL}, "value")
    )
    def on_add_click(add_filter_n_clicks, filter_slider, filter_dropdown):

        add_filter_features = filter_dropdown
        selected_bounds = np.array(filter_slider).reshape(-1, 2)

        _, new_df = create_table_df(
            dataframe,
            add_filter_n_clicks,
            add_filter_features,
            selected_bounds
        )

        csv_string = new_df.to_csv(index=False, encoding="utf-8")
        csv_string = "data:text/csv;charset=utf-8,%EF%BB%BF" + urllib.parse.quote(csv_string)
   
        # Shuffle dataframe
        new_df = new_df.sample(frac=1)
        new_df.to_dict("records"), csv_string
        return new_df.to_dict("records"), csv_string

    app.run_server(debug=True)

if __name__ == "__main__":
    external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
    app = dash.Dash("__main__", external_stylesheets=external_stylesheets)
    main(dataframe = read(config.SCHEMA_FILE, config.DATA_FILE))