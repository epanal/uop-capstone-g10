from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
from spiderChart import spider_callback, spider_layout
from lineChart import line_callback, line_layout
from datetime import datetime

# Initialize the app with Bootstrap theme
app = Dash(__name__, title = 'Patient Assessment Dashboard', external_stylesheets=[dbc.themes.CYBORG])

# App layout with centered dropdowns and plots
app.layout = dbc.Container(
    [
        html.Br(),
        dbc.Row(
            dbc.Col(
                html.H2(
                    "🩺 Patient Assessment Dashboard",
                    className="text-center text-white",
                ),
                width=12,
            )
        ),
        html.Div(
            f"Current Date: {datetime.now().strftime('%A, %B %d, %Y %I:%M %p')}",
            className="text-center text-white",
        ),
        html.Hr(),
        dbc.Tabs(
            [
            dbc.Tab(label="Radar Chart", children=[
                spider_layout
                ]),
            dbc.Tab(label="Line Chart", children=[
                line_layout
                ]),
            ],
        id="tabs",
        active_tab="Radar Chart",
        ),
        html.Div(id="tab-content", className="p-4"),
    ]
)

spider_callback(app)
line_callback(app)

@app.callback(
    Output("tab-content", "children"),
    Input("tabs", "active_tab")
)

def render_tab_content(active_tab):
    if active_tab == "Radar Chart":
        return spider_callback(app)
    elif active_tab == "Line Chart":
        return line_callback(app)
    return html.Div("Choose a tab to read")

# Run the app
if __name__ == "__main__":
    app.run(debug=True)