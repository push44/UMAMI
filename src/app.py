import config

import pickle
import dash
import numpy as np
import pandas as pd
import plotly.express as px
import dash_core_components as dcc
import dash_html_components as html

from dash.dependencies import Input
from dash.dependencies import Output


def main(schema_file, data_file):

    def read(schema_file, data_file):
        with open(schema_file, "rb") as file:
            # List of 39 dictionaries each with keys name, type, baseType
            schema = pickle.load(file)
        with open(data_file, "rb") as file:
            # List of lists with shape 1987 x 39
            data = pickle.load(file)
            data = np.array(data)

        schema_names = list(map(lambda dictionary: dictionary["name"], schema))
        
        content = {}
        for ind, name in enumerate(schema_names):
            content[name] = list(data[:, ind])

        return pd.DataFrame(content)

    def create_layout(df):

        return html.Div(
            children=[
                html.H1(children = "Uncertainty Managed Access to Microstructures Interface Project",
                style={'textAlign': 'center'}),
                html.Div([
                    html.Div([dcc.Dropdown(
                        id = "xaxis-column",
                        options = [{'label': col, 'value': col} for col in df.columns[2:]],
                        value = "ABS_wf_D",
                    )]),
                    html.Div([dcc.Dropdown(
                        id = "yaxis-column",
                        options = [{'label': col, 'value': col} for col in df.columns[2:]],
                        value = "STAT_CC_D",
                    )])
                ]),
                dcc.Graph(id='indicator-graphic')
            ])

    #####################################################################
    dataframe = read(schema_file, data_file)

    external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
    app = dash.Dash("__main__", external_stylesheets=external_stylesheets)
    app.layout = create_layout(dataframe)

    #####################################################################

    @app.callback(
        Output("indicator-graphic", "figure"),
        Input("xaxis-column", "value"),
        Input("yaxis-column", "value"))
    def update_output(xaxis_column_name, yaxis_column_name):
        fig = px.scatter(dataframe, x=xaxis_column_name, y=yaxis_column_name)
        return fig

    app.run_server(debug=True)

if __name__ == "__main__":
    main(config.SCHEMA_FILE, config.DATA_FILE)
