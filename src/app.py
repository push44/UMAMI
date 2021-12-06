import config
import json
import dash
import urllib.parse
import plotly.express as px
import numpy as np

from dash.dependencies import Input
from dash.dependencies import Output
from dash.dependencies import State
from dash.dependencies import ALL

from read import read
from layout import create_new_dropdown_div
from layout import create_layout
from layout import create_table_df
from layout import thresholds

def main(dataframe):
    # Get app layout
    app.layout = create_layout(dataframe)

    ############################## Update Slider ##############################
    # x axis
    @app.callback(
        Output("my-range-slider-x", "min"),
        Input("xaxis-column", "value")
    )
    def update_xaxis_min(xaxis_column):
        return dataframe[xaxis_column].min()

    @app.callback(
        Output("my-range-slider-x", "max"),
        Input("xaxis-column", "value")
    )
    def update_xaxis_max(xaxis_column):
        return dataframe[xaxis_column].max()

    @app.callback(
        Output("my-range-slider-x", "value"),
        Input("xaxis-column", "value") 
    )
    def update_xaxis_value(xaxis_column):
        range = [dataframe[xaxis_column].min(), dataframe[xaxis_column].max()]
        return range

    # y axis
    @app.callback(
        Output("my-range-slider-y", "min"),
        Input("yaxis-column", "value")
    )
    def update_yaxis_min(yaxis_column):
        return dataframe[yaxis_column].min()

    @app.callback(
        Output("my-range-slider-y", "max"),
        Input("yaxis-column", "value")
    )
    def update_yaxis_max(yaxis_column):
        return dataframe[yaxis_column].max()

    @app.callback(
        Output("my-range-slider-y", "value"),
        Input("yaxis-column", "value") 
    )
    def update_yaxis_value(yaxis_column):
        range = [dataframe[yaxis_column].min(), dataframe[yaxis_column].max()]
        return range

    ############################## Update Scatter Plot ##############################
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

    ############################## Update Dropdown (Add filter) ##############################
    # Initiate empty-dropdown after every click event (n_clicks type) by
    # component_id = add-filter.
    @app.callback(
        Output("dropdown-container", "children"),
        Input("add-filter", "n_clicks"),
        State("dropdown-container", "children")
    )
    def display_dropdown(button_click, dropdown_children_state):
        # If click event has occured then create new dropdown menue to add next filter
        # These dropdown menues are indexed over button_click (click event number)
        new_dropdown_div = create_new_dropdown_div(button_click, dataframe.columns[2:])
        # Return list of dropdown objects (In sequence)
        dropdown_children_state.append(new_dropdown_div)

        return dropdown_children_state

    ############################## Update Dropdown (Remove filter) ##############################
    # Initiate empty-dropdown after every click event (n_clicks type) by
    # component_id = add-filter.
    """@app.callback(
        Output("dropdown-container-remove", "children"),
        Input("remove-filter", "n_clicks"),
        State("dropdown-container-remove", "children")
    )
    def display_dropdown(button_click, dropdown_children_state):
        # If click event has occured then create new dropdown menue to add next filter
        # These dropdown menues are indexed over button_click (click event number)
        new_dropdown_div = create_new_dropdown_div(button_click, dataframe.columns[2:], False)
        # Return list of dropdown objects (In sequence)
        dropdown_children_state.append(new_dropdown_div)

        return dropdown_children_state"""

    ############################## Update Table (Add filter) ##############################
    # Initialize table to count out-of-range-values
    # Update table (sort by out-of-range-values desc) immediately after 
    # click event has occured
    #Output("table-id", "data"),
    #Input("remove-filter", "n_clicks"),
    #remove_filter_n_clicks,
    #State({'type': 'filter-dropdown-remove', 'index': ALL}, 'value'),
    #remove_filter_dropdown_state
    @app.callback(
        Output("table-id", "data"),
        Output("download-link", "href"),
        Input("add-filter", "n_clicks"),
        State({'type': 'filter-dropdown-add', 'index': ALL}, 'value'),
        State({'type': 'number', 'index': ALL}, 'value')
    )
    def on_add_click(add_filter_n_clicks, add_filter_dropdown_state, limits_state):

        add_filter_features = add_filter_dropdown_state
        selected_bounds = np.array(limits_state).reshape(-1, 2)
        #remove_filter_features = remove_filter_dropdown_state
        # Create table to be rendered
        #remove_filter_features
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
        return new_df.to_dict("records"), csv_string

    app.run_server(debug=True)

if __name__ == "__main__":
    external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
    app = dash.Dash("__main__", external_stylesheets=external_stylesheets)
    main(dataframe = read(config.SCHEMA_FILE, config.DATA_FILE))
