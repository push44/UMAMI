import config
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
    app.layout = create_layout(dataframe.columns)

    ############################## Update Scatter Plot ##############################
    # At first initialize scatter plot with the default values
    # Update the plot (with out any click) if any Input variable values are updated
    # Output figure to component_id = indicator-graphic with figure prperty
    @app.callback(
        Output("indicator-graphic", "figure"),
        Input("xaxis-column", "value"),
        Input("lbx", "value"),
        Input("ubx", "value"),
        Input("yaxis-column", "value"),
        Input("lby", "value"),
        Input("uby", "value")
    )
    def update_output(
        xaxis_column_name,
        lbx,
        ubx,
        yaxis_column_name,
        lby,
        uby):

        # Update the dataframe based on given bounds
        upadted_dataframe = thresholds(
            dataframe,
            xaxis_column_name,
            yaxis_column_name,
            lbx,
            ubx,
            lby,
            uby
        )

        # Create scatter plot
        fig = px.scatter(upadted_dataframe, x=xaxis_column_name, y=yaxis_column_name)
        return fig


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
    @app.callback(
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

        return dropdown_children_state

    ############################## Update Table (Add filter) ##############################
    # Initialize table to count out-of-range-values
    # Update table (sort by out-of-range-values desc) immediately after 
    # click event has occured
    @app.callback(
        Output("table-id", "data"),
        Output("table-head-id", "data"),
        Output("download-link", "href"),
        Input("add-filter", "n_clicks"),
        Input("remove-filter", "n_clicks"),
        State({'type': 'filter-dropdown-add', 'index': ALL}, 'value'),
        State({'type': 'filter-dropdown-remove', 'index': ALL}, 'value'),
        State({'type': 'number', 'index': ALL}, 'value')
    )
    def on_add_click(add_filter_n_clicks, remove_filter_n_clicks, add_filter_dropdown_state, remove_filter_dropdown_state, limits_state):

        add_filter_features = add_filter_dropdown_state
        selected_bounds = np.array(limits_state).reshape(-1, 2)
        remove_filter_features = remove_filter_dropdown_state
        # Create table to be rendered
        table_df, new_df = create_table_df(
            dataframe,
            add_filter_n_clicks,
            add_filter_features,
            selected_bounds,
            remove_filter_features
        )

        csv_string = new_df.to_csv(index=False, encoding="utf-8")
        csv_string = "data:text/csv;charset=utf-8,%EF%BB%BF" + urllib.parse.quote(csv_string)
   
        # Shuffle dataframe
        new_df = new_df.sample(frac=1)
        return table_df.to_dict("records"), new_df.to_dict("records"), csv_string

    app.run_server(debug=False)

if __name__ == "__main__":
    external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
    app = dash.Dash("__main__", external_stylesheets=external_stylesheets)
    main(dataframe = read(config.SCHEMA_FILE, config.DATA_FILE))
