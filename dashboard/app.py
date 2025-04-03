from dash import Dash, html, dash_table, dcc, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from spiderChart import spider
from lineChart import time_series


# Function to format date columns
def clean_dates(col):
    return pd.to_datetime(col.str.split('M').str[0], format='mixed').dt.round('h')


def clean_df(df):
    # Format the date values, rounding to the hour
    df['assessment_date'] = clean_dates(df['assessment_date'])
    # Calculate assessment scores
    df['score'] = df.iloc[:, 3:].sum(axis=1)
    # Sort rows based on assessment date at the hour
    df = df.sort_values(['initial_group_identifier', 'assessment_date'])
    # Round assessment date to the day
    df['assessment_date'] = df['assessment_date'].dt.round('d')
    # Drop extra rows from days patients did multiple assessments
    df = df.drop_duplicates(subset=['initial_group_identifier', 'assessment_date'], keep='last')
    return df


# Reading data
who = pd.read_csv("data/who_merged.csv")
gad = pd.read_csv("data/gad_merged.csv")
phq = pd.read_csv("data/phq_merged.csv")
pcl = pd.read_csv("data/ptsd_merged.csv")
ders = pd.read_csv("data/ders_merged.csv")
ders2 = pd.read_csv('data/ders2_merged.csv')

# Cleaning data
who = clean_df(who)
phq = clean_df(phq)
pcl = clean_df(pcl)

# GAD
gad['5. * Being so restless that it is too hard to sit still'] = gad[
    '5. * Being so restless that it is too hard to sit still'].combine_first(
    gad['5. * Being so restless that it’s hard to sit still'])
gad.drop('5. * Being so restless that it’s hard to sit still', inplace=True, axis=1)
gad = clean_df(gad)

# DERS2
reversed_questions = [1, 2, 6, 7, 8, 10, 17, 20, 22, 24, 34]
reversed_elements = [str(x) for x in reversed_questions]
reverse_cols = ders2.loc[:, ders2.columns.str.split('.').str[0].isin(reversed_elements)].columns
mapping = {"'-1": 1, "'-2": 2, "'-3": 3, "'-4": 4, "'-5": 5}
ders2[reverse_cols] = ders2[reverse_cols].apply(lambda x: x.map(mapping))

# Combining DERS files
ders2.columns = ders.columns
ders = pd.concat([ders, ders2])
ders = clean_df(ders)

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

# Current date
now = datetime.now()

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
            f"Today is {now.strftime('%B')} {now.strftime('%d')}"
            f", {now.strftime('%Y')}", className="text-white text-center"
        ),
        html.Hr(),
        dbc.Tabs(
            [
                # Title Page
                dbc.Tab(
                    label="Title Page",
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
                                                id="table-patient-select",
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
                                        dcc.Graph(
                                            id="exam-scores",
                                            style={
                                                "height": "70vh",
                                                "width": "80%",
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


# Callbacks for title page
@app.callback(
    Output("exam-scores", "figure"),
    [
        Input("table-patient-select", "value")
    ],
)
def update_exam_scores(patient_id):
    table_data = df.copy()
    table_data['assessment_date'] = table_data['assessment_date'].dt.strftime('%Y-%m-%d')
    fig = go.Figure(data=[go.Table(
        header=dict(values=["Initial Group Identifier", "Assessment Date"] + assessments,
                    line_color='darkslategray',
                    fill_color='paleturquoise',
                    align='left'),
        cells=dict(values=table_data[
            table_data.initial_group_identifier == patient_id
            ].transpose().values.tolist(),
                   line_color='darkslategray',
                   fill_color='lavender',
                   align='right'))
    ])
    return fig


# Callbacks for Spider Chart
@app.callback(
    Output("spider-chart", "figure"),
    [
        Input("spider-patient-select", "value")
    ],
)
def update_spider_chart(patient_id):
    return spider(
        scores,
        totals + totals[:1],
        assessments + assessments[:1],
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
