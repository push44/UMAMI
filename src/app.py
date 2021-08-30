import config
import dash
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
    app.layout = create_layout(dataframe.columns)

    ############################## Update Scatter Plot ##############################
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

        lbx, lby = list(map(lambda val: -1000 if val==None else val, (lbx, lby)))
        ubx, uby = list(map(lambda val: 1000 if val==None else val, (ubx, uby)))

        upadted_dataframe = thresholds(
            dataframe,
            xaxis_column_name,
            yaxis_column_name,
            lbx,
            ubx,
            lby,
            uby
        )

        fig = px.scatter(upadted_dataframe, x=xaxis_column_name, y=yaxis_column_name)
        return fig


    ############################## Update Dropdown ##############################
    @app.callback(
        Output("dropdown-container", "children"),
        Input("add-filter", "n_clicks"),
        State("dropdown-container", "children")
    )
    def display_dropdown(button_click, dropdown_children_state):
        new_dropdown_div = create_new_dropdown_div(button_click, dataframe.columns[2:])
        dropdown_children_state.append(new_dropdown_div)

        return dropdown_children_state

    @app.callback(
        Output("table-id", "data"),
        Input("add-filter", "n_clicks"),
        State({'type': 'filter-dropdown', 'index': ALL}, 'value'),
        State({'type': 'number', 'index': ALL}, 'value')
    )
    def on_click(number_of_times_button_has_clicked, filter_dropdown_state, filter_limits_state):
        selected_features = filter_dropdown_state
        selected_bounds = np.array(filter_limits_state).reshape(-1, 2)
        table_df = create_table_df(
            dataframe,
            number_of_times_button_has_clicked,
            selected_features,
            selected_bounds
        )
        return table_df.to_dict("records")

    app.run_server(debug=True)

if __name__ == "__main__":
    external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
    app = dash.Dash("__main__", external_stylesheets=external_stylesheets)
    main(read(config.SCHEMA_FILE, config.DATA_FILE))
