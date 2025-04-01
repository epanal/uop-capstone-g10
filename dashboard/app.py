from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
from spiderChart import spider
from lineChart import time_series


# Function to format date columns
def clean_dates(col):
    return pd.to_datetime(col.str.split(" ").str[0], format="mixed")


# Reading data
who = pd.read_csv("data/who_merged.csv")
gad = pd.read_csv("data/gad_merged.csv")
phq = pd.read_csv("data/phq_merged.csv")
pcl = pd.read_csv("data/ptsd_merged.csv")
ders = pd.read_csv("data/ders_merged.csv")

# Cleaning data (same as before)
# WHO

who["assessment_date"] = clean_dates(who["assessment_date"])
who["score"] = who.iloc[:, -5:].sum(axis=1)
who.sort_values(["initial_group_identifier", "assessment_date"], inplace=True)

# GAD

gad["assessment_date"] = clean_dates(gad["assessment_date"])
gad["5. * Being so restless that it is too hard to sit still"] = gad[
    "5. * Being so restless that it is too hard to sit still"
].combine_first(gad["5. * Being so restless that it’s hard to sit still"])
gad.drop("5. * Being so restless that it’s hard to sit still", inplace=True, axis=1)
gad["score"] = gad.iloc[:, -7:].sum(axis=1)
gad.sort_values(["initial_group_identifier", "assessment_date"], inplace=True)

# PHQ

phq["assessment_date"] = clean_dates(phq["assessment_date"])
phq["score"] = phq.iloc[:, -9:].sum(axis=1)
phq.sort_values(["initial_group_identifier", "assessment_date"], inplace=True)

# PCL

pcl["assessment_date"] = clean_dates(pcl["assessment_date"])
pcl["score"] = pcl.iloc[:, -20:].sum(axis=1)
pcl.sort_values(["initial_group_identifier", "assessment_date"], inplace=True)

# DERS

ders["assessment_date"] = clean_dates(ders["assessment_date"])
ders["score"] = ders.iloc[:, -36:].sum(axis=1)
ders.sort_values(["initial_group_identifier", "assessment_date"], inplace=True)

# Combine all assessment data into one dataframe
cols = ["initial_group_identifier", "assessment_date", "score"]
assessments = ["WHO", "GAD", "PHQ", "PCL", "DERS"]
df = who[cols].merge(
    gad[cols],
    how="outer",
    on=["initial_group_identifier", "assessment_date"],
    suffixes=("_WHO", "_GAD"),
)
df = df.merge(
    phq[cols],
    how="outer",
    on=["initial_group_identifier", "assessment_date"],
    suffixes=(None, "_PHQ"),
)
df = df.merge(
    pcl[cols],
    how="outer",
    on=["initial_group_identifier", "assessment_date"],
    suffixes=(None, "_PCL"),
)
df = df.merge(
    ders[cols],
    how="outer",
    on=["initial_group_identifier", "assessment_date"],
    suffixes=(None, "_DERS"),
)
df.columns = ["initial_group_identifier", "assessment_date"] + assessments

scores = df.groupby("initial_group_identifier")[assessments].mean()

# Total possible score for each assessment
totals = [25.0, 21.0, 27.0, 80.0, 180.0]

# Initialize the app with Bootstrap theme
app = Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])

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
            "Current Date: Friday, March 28, 2025", className="text-white text-center"
        ),
        html.Hr(),
        dbc.Tabs(
            [
                # Spider Chart Tab
                dbc.Tab(
                    label="Spider Chart",
                    children=[
                        html.Br(),
                        dbc.Row(
                            dbc.Col(
                                [
                                    html.Div(
                                        [
                                            html.Label(
                                                "Select Patient:",
                                                className="text-white",
                                            ),
                                            dcc.Dropdown(
                                                id="spider-patient-select",
                                                options=[
                                                    {"label": pid, "value": pid}
                                                    for pid in scores.index
                                                ],
                                                value=scores.index[0],
                                                clearable=False,
                                            ),
                                        ],
                                        style={"width": "50%", "margin": "auto"},
                                    ),
                                    html.Div(
                                        [
                                            html.Label(
                                                "Select Assessment:",
                                                className="text-white",
                                            ),
                                            dcc.Dropdown(
                                                id="spider-assessment-select",
                                                options=[
                                                    {"label": name, "value": name}
                                                    for name in assessments
                                                ],
                                                value=assessments[0],
                                                clearable=False,
                                            ),
                                        ],
                                        style={"width": "50%", "margin": "auto"},
                                    ),
                                    html.Div(
                                        dcc.Graph(
                                            id="spider-chart",
                                            style={
                                                "height": "70vh",
                                                "width": "50%",
                                                "margin": "auto",
                                            },
                                        ),
                                    ),
                                ],
                                width=12,
                            )
                        ),
                    ],
                ),
                # Line Chart Tab
                dbc.Tab(
                    label="Line Chart",
                    children=[
                        html.Br(),
                        dbc.Row(
                            dbc.Col(
                                [
                                    html.Div(
                                        [
                                            html.Label(
                                                "Select Patient:",
                                                className="text-white",
                                            ),
                                            dcc.Dropdown(
                                                id="line-patient-select",
                                                options=[
                                                    {"label": pid, "value": pid}
                                                    for pid in df[
                                                        "initial_group_identifier"
                                                    ].unique()
                                                ],
                                                value=df[
                                                    "initial_group_identifier"
                                                ].unique()[0],
                                                clearable=False,
                                            ),
                                        ],
                                        style={"width": "50%", "margin": "auto"},
                                    ),
                                    html.Div(
                                        [
                                            html.Label(
                                                "Select Assessment:",
                                                className="text-white",
                                            ),
                                            dcc.Dropdown(
                                                id="line-assessment-select",
                                                options=[
                                                    {"label": name, "value": name}
                                                    for name in assessments
                                                ],
                                                value=assessments[0],
                                                clearable=False,
                                            ),
                                        ],
                                        style={"width": "50%", "margin": "auto"},
                                    ),
                                    html.Div(
                                        dcc.Graph(
                                            id="line-chart",
                                            style={
                                                "height": "70vh",
                                                "width": "50%",
                                                "margin": "auto",
                                            },
                                        ),
                                    ),
                                ],
                                width=12,
                            )
                        ),
                    ],
                ),
            ]
        ),
    ],
    fluid=True,
)


# Callbacks for Spider Chart
@app.callback(
    Output("spider-chart", "figure"),
    [
        Input("spider-patient-select", "value"),
        Input("spider-assessment-select", "value"),
    ],
)
def update_spider_chart(patient_id, assessment):
    return spider(
        scores,
        totals,
        assessments,
        patient_id,
        f"Assessment Scores for Patient: {patient_id}",
    )


# Callbacks for Line Chart
@app.callback(
    Output("line-chart", "figure"),
    [Input("line-patient-select", "value"), Input("line-assessment-select", "value")],
)
def update_line_chart(patient_id, assessment):
    return time_series(df, assessment, patient_id)


# Run the app
if __name__ == "__main__":
    app.run(debug=True)
