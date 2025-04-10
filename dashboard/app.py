from dash import Dash, html, dash_table, dcc, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from spiderChart import spider
from lineChart import time_series
from wordCloud import generate_wordcloud
from bps_charts import generate_bps_figure, generate_sunburst_chart
from php_daily import sparkline_figure, wordcloud_figure, craving_line_chart
import json
import os

# Load configuration from config.json
with open('config.json', 'r') as config_file:
    config = json.load(config_file)
data_directory = config['data_directory']


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
who = pd.read_csv(os.path.join(data_directory, 'who_merged.csv'))
gad = pd.read_csv(os.path.join(data_directory, "gad_merged.csv"))
phq = pd.read_csv(os.path.join(data_directory, "phq_merged.csv"))
pcl = pd.read_csv(os.path.join(data_directory, "ptsd_merged.csv"))
ders = pd.read_csv(os.path.join(data_directory, "ders_merged.csv"))
ders2 = pd.read_csv(os.path.join(data_directory, "ders2_merged.csv"))
bps = pd.read_csv(os.path.join(data_directory, "bps_anonimized.csv"))
php_daily = pd.read_csv(os.path.join(data_directory, "extracted_php_assessments.csv"))
sub_history = pd.read_csv(os.path.join(data_directory, 'patient_substance_history.csv'))

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

# BPS
bps_column_mapping = {
    'bps_medical': 'Medical', 'bps_employment': 'Employment', 'bps_peer_support': 'Peer Support',
    'bps_drug_alcohol': 'Drug/Alcohol Usage', 'bps_legal': 'Legal', 'bps_family': 'Family/Social',
    'bps_mh': 'Mental Health', 'bps_total': 'Total', 'bps_problems': 'Problems'
}
bps_df = bps.rename(columns=bps_column_mapping)

all_internal_motivation = " ".join(bps_df['int_motivation'].dropna())
all_external_motivation = " ".join(bps_df['ext_motivation'].dropna())
internal_wc = generate_wordcloud(all_internal_motivation, "Internal Motivation", "Blues")
external_wc = generate_wordcloud(all_external_motivation, "External Motivation", "Oranges")

# df for rows where use_flag = 1
used_substances = sub_history[sub_history['use_flag'] == 1]

# total number of unique patients
total_patients = sub_history['group_identifier'].nunique()

# Group the data by substance and pattern of use, counting the number of occurrences
used_substances_grouped = used_substances[used_substances['use_flag'] == 1] \
    .groupby(['substance', 'pattern_of_use_consolidated']) \
    .size() \
    .reset_index(name='count')

# substance-level percentages (inner circle)
substance_totals = used_substances_grouped.groupby('substance')['count'].sum().reset_index()
substance_totals['percentage'] = (substance_totals['count'] / total_patients) * 100

# pattern-level percentages (outer circle)
used_substances_grouped['percentage'] = (used_substances_grouped['count'] / total_patients) * 100
# Generate the Sunburst figure
sunburst_fig = generate_sunburst_chart(used_substances_grouped, total_patients)

# Combine all industry standard assessment data into one dataframe
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
                    tab_id="tab-0",
                    children=[
                        html.Br(),
                        html.Div(
                            [
                                html.H4("Patient Motivation Word Clouds",
                                        className="text-white bg-dark p-2 rounded",
                                        style={'textAlign': 'center'})
                            ], style={"width": "50%", "margin": "auto"},
                        ),
                        dbc.Row([
                            dbc.Col([
                                html.Img(src=f"data:image/png;base64,{internal_wc}",
                                         style={'width': '100%', 'height': 'auto', 'borderRadius': '8px'})
                            ], width={"size": 5}, align="center"),
                            dbc.Col([
                                html.Img(src=f"data:image/png;base64,{external_wc}",
                                         style={'width': '100%', 'height': 'auto', 'borderRadius': '8px'})
                            ], width={"size": 5}, align="center")
                        ], align="center", justify="center")
                    ],
                ),
                # Assessment Scores Table
                dbc.Tab(
                    label="🔢 Assessment Scores",
                    tab_id="tab-1",
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
                                                id="assessment-table-patient-select",
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
                                                "Select Patient:",
                                                className="text-white",
                                            ),
                                        ],
                                        style={"width": "50%", "margin": "auto"},
                                    ),
                                    html.Div(
                                        dash_table.DataTable(
                                            id='assessment-scores',
                                            data=df.to_dict('records'),
                                            columns=[
                                                {'name': 'Initial Group Identifier'
                                                    , 'id': 'initial_group_identifier', 'type': 'text'},
                                                {'name': 'Assessment Date'
                                                    , 'id': 'assessment_date', 'type': 'datetime'},
                                                {'name': 'WHO', 'id': 'WHO', 'type': 'numeric'},
                                                {'name': 'GAD', 'id': 'GAD', 'type': 'numeric'},
                                                {'name': 'PHQ', 'id': 'PHQ', 'type': 'numeric'},
                                                {'name': 'PCL', 'id': 'PCL', 'type': 'numeric'},
                                                {'name': 'DERS', 'id': 'DERS', 'type': 'numeric'},
                                            ],
                                            style_cell_conditional=[
                                                {
                                                    'if': {'column_id': c},
                                                    'textAlign': 'left'
                                                } for c in df.columns
                                            ],
                                            editable=True,
                                            style_filter={'backgroundColor': 'black'},
                                            style_cell={'backgroundColor': 'black', 'color': 'white',
                                                        'fontSize': 16, 'font-family': 'sans-serif'},
                                            style_header={
                                                'backgroundColor': 'rgb(30, 30, 30)',
                                                'color': 'white'
                                            },
                                            style_data={
                                                'backgroundColor': 'rgb(50, 50, 50)',
                                                'color': 'white'
                                            },
                                            page_size=10,
                                            style_data_conditional=(
                                                    [
                                                        {
                                                            'if': {
                                                                'filter_query': '0 < {{{}}} < {}'.format(col, value),
                                                                'column_id': col
                                                            },
                                                            'backgroundColor': '#FF4136',
                                                            'color': 'white'
                                                        } for col, value in zip(df[assessments].quantile(0.5).index,
                                                                                df[assessments].quantile(
                                                                                    0.5).to_numpy())
                                                    ] +
                                                    [
                                                        {
                                                            'if': {
                                                                'filter_query': '{{{}}} >= {}'.format(col, value),
                                                                'column_id': col
                                                            },
                                                            'backgroundColor': '#3D9970',
                                                            'color': 'white'
                                                        } for col, value in zip(df[assessments].quantile(0.5).index,
                                                                                df[assessments].quantile(
                                                                                    0.5).to_numpy())
                                                    ]
                                            )
                                        ),
                                        style={"width": "50%", "margin": "auto"},
                                    ),
                                ],
                                width=12,
                            )
                        ),
                    ],
                ),
                # Spider Chart Tab
                dbc.Tab(
                    label="🕸️ Spider Chart",
                    tab_id="tab-2",
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
                    label="📈 Line Chart",
                    tab_id="tab-3",
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
                # Biopsychosocial Assessment Tab
                dbc.Tab(
                    label="📈 Biopsychosocial Assessment",
                    tab_id="tab-4",
                    children=[
                        html.Br(),
                        dbc.Row(
                            dbc.Col(
                                [
                                    # Sunburst chart
                                    html.Div(  # Wrap in a div for consistency with other tabs
                                        dcc.Graph(
                                            id="sunburst-chart",
                                            figure=sunburst_fig,
                                            style={
                                                "height": "70vh",
                                                "width": "50%",  # Same as spider and line charts
                                                "margin": "auto",
                                                "display": "block",
                                            },
                                        ),
                                        style={"width": "50%", "margin": "auto"},  # Match dropdown container
                                    ),
                                    # Patient filter dropdown
                                    html.Div(
                                        [
                                            html.Label(
                                                "Select Patient:",
                                                className="text-white",
                                            ),
                                            dcc.Dropdown(
                                                id="bps-patient-dropdown",
                                                options=[
                                                    {"label": pid, "value": pid}
                                                    for pid in bps_df["group_identifier"].unique()
                                                ],
                                                value=bps_df["group_identifier"].iloc[0],
                                                clearable=False,
                                            ),
                                        ],
                                        style={"width": "50%", "margin": "auto"},
                                    ),
                                    html.Div(
                                        id="bps-content",
                                        style={"width": "50%", "margin": "auto", "margin-top": "20px"},
                                    ),
                                ],
                                width=12,
                            )
                        ),
                    ],
                ),
                # PHP Daily Assessments
                dbc.Tab(
                    label="📊 PHP Daily Assessments",
                    tab_id="tab-5",
                    children=[
                        html.Br(),
                        dbc.Row(
                            dbc.Col(
                                [
                                    # Patient selection dropdown
                                    html.Div(
                                        [
                                            html.Label(
                                                "Select Patient:",
                                                className="text-white",
                                            ),
                                            dcc.Dropdown(
                                                id="php-patient-dropdown",
                                                options=[
                                                    {"label": pid, "value": pid}
                                                    for pid in php_daily["group_identifier"].unique()
                                                ],
                                                value=php_daily["group_identifier"].iloc[0],
                                                clearable=False,
                                            ),
                                        ],
                                        style={"width": "50%", "margin": "auto"},
                                    ),
                                    # Category selection dropdown
                                    html.Div(
                                        [
                                            html.Label(
                                                "Select Data Category:",
                                                className="text-white",
                                            ),
                                            dcc.RadioItems(
                                                id="php-category-select",
                                                options=[
                                                    {"label": "Moods", "value": "Moods"},
                                                    {"label": "Supports", "value": "Supports"},
                                                    {"label": "Skills", "value": "Skills"},
                                                    {"label": "Craving", "value": "Craving"},
                                                ],
                                                value="Moods",  # Default selection
                                                labelStyle={'display': 'inline-block', 'margin-right': '20px'},
                                            ),
                                        ],
                                        style={"width": "50%", "margin": "auto", "marginBottom": "20px"},
                                    ),
                                    # Containers for the figure and wordcloud
                                    html.Div(id="php-wordcloud-content", children=[]),
                                    html.Div(
                                        id="php-assessment-content",  # Content will be updated by the callback
                                        style={"width": "50%", "margin": "auto", "margin-top": "20px"},
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
# @app.callback(
#     Output("word-cloud", "figure"),
#     [Input(None, None)]
# )
# def update_word_cloud():
#     all_internal_motivation = " ".join(bps_df['int_motivation'].dropna())
#     all_external_motivation = " ".join(bps_df['ext_motivation'].dropna())
#     internal_wc = generate_wordcloud(all_internal_motivation, "Internal Motivation", "Blues")
#     external_wc = generate_wordcloud(all_external_motivation, "External Motivation", "Oranges")
#     return


# Callbacks for Assessment Scores Table
@app.callback(
    Output("assessment-scores", "data"),
    [Input("assessment-table-patient-select", "value")],
)
def update_data_table(patient_id):
    table_data = df.copy()
    table_data['assessment_date'] = table_data['assessment_date'].dt.strftime('%Y-%m-%d')
    return table_data[table_data.initial_group_identifier == patient_id].to_dict('records')


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


# Callback for BPS Chart
@app.callback(
    Output('bps-content', 'children'),
    [Input('bps-patient-dropdown', 'value')]
)
def update_bps_content(patient_id):
    # Filter the patient data for BPS
    filtered_df = bps_df[bps_df['group_identifier'] == patient_id]
    patient_info = filtered_df[['group_identifier', 'age', 'int_motivation', 'ext_motivation']].drop_duplicates().iloc[
        0]

    # Biopsychosocial aggregate and individual scores
    bps_cols = [col for col in bps_column_mapping.values() if col != "Total"]
    bps_aggregates = bps_df[bps_cols].agg(['mean', 'median']).transpose()
    individual_scores = filtered_df[bps_cols].iloc[0]
    patient_ban = filtered_df[bps_cols].sum(axis=1).iloc[0]
    total_bps_avg = bps_df[bps_cols].sum(axis=1).mean()

    # Create BPS figure
    fig = generate_bps_figure(bps_df, bps_column_mapping, patient_id)

    # Filter sub_history for the selected patient and use_flag == 1
    filtered_sub_history = sub_history[
        (sub_history['group_identifier'] == patient_id) &
        (sub_history['use_flag'] == 1)
        ]

    # Define columns to display (exclude index and 'pattern_of_use', include 'pattern_of_use_consolidated')
    display_columns = [col for col in filtered_sub_history.columns if col not in ['pattern_of_use']]

    # Create DataTable for filtered sub_history
    if not filtered_sub_history.empty:
        sub_history_table = dash_table.DataTable(
            data=filtered_sub_history[display_columns].to_dict('records'),
            columns=[{"name": col, "id": col} for col in display_columns],
            style_table={
                'overflowX': 'auto',  # Horizontal scroll if needed
                'marginTop': '20px',
            },
            style_cell={
                'textAlign': 'left',
                'color': 'white',  # Text color matches CYBORG theme
                'backgroundColor': '#1a1a1a',  # Dark background
                'padding': '5px',
            },
            style_header={
                'backgroundColor': '#343a40',  # Darker header like CYBORG
                'fontWeight': 'bold',
                'color': 'white',
            },
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': '#212529',  # Slightly lighter for odd rows
                }
            ],
            sort_action='native',  # Enable sorting
        )
    else:
        sub_history_table = html.P("No substance use history (use_flag=1) available for this patient.",
                                   className="text-white")

    return html.Div([
        html.H4("Patient Overview", className="text-white bg-dark p-2 rounded"),
        html.P(f"Patient ID: {patient_info['group_identifier']}", className="text-white"),
        html.P(f"Age: {patient_info['age']}", className="text-white"),
        html.P(f"Internal Motivation: {patient_info['int_motivation']}", className="text-white"),
        html.P(f"External Motivation: {patient_info['ext_motivation']}", className="text-white"),
        html.H4("Biopsychosocial Scores", className="text-white bg-dark p-2 rounded mt-4"),
        html.Div([
            html.Span(f"Patient's Total: {round(patient_ban, 2)}", style={'color': '#FF5722', 'margin-right': '20px'}),
            html.Span(f"Average Total (All Patients): {round(total_bps_avg, 1)}", style={'color': '#00BCD4'})
        ], className="mb-3"),
        dcc.Graph(figure=fig),
        html.H4("Substance Use History", className="text-white bg-dark p-2 rounded mt-4"),
        sub_history_table
    ])


@app.callback(
    [Output("php-assessment-content", "children"),
     Output("php-wordcloud-content", "children")],
    [Input("php-patient-dropdown", "value"),
     Input("php-category-select", "value")]
)
def update_php_assessment(selected_patient_id, category):
    # Based on the category selection, call the appropriate functions.
    if category == "Moods":
        fig = sparkline_figure(php_daily, selected_patient_id, 'moods')
        wordcloud_img_path = wordcloud_figure(php_daily, selected_patient_id, 'mood')
        wordcloud_component = html.Div(
            [
                html.H4("Patient's common words:", className="text-white text-center", style={'marginBottom': '50px'}),
                html.Img(src=wordcloud_img_path, style={'maxWidth': '80%', 'margin': '0 auto', 'display': 'block'}),
            ],
            style={'textAlign': 'center', 'marginTop': '50px', 'marginBottom': '50px'},
        )
    elif category == "Supports":
        fig = sparkline_figure(php_daily, selected_patient_id, 'supports')
        wordcloud_img_path = wordcloud_figure(php_daily, selected_patient_id, 'support')
        wordcloud_component = html.Div(
            [
                html.H4("Patient's support keywords:", className="text-white text-center",
                        style={'marginBottom': '50px'}),
                html.Img(src=wordcloud_img_path, style={'maxWidth': '80%', 'margin': '0 auto', 'display': 'block'}),
            ],
            style={'textAlign': 'center', 'marginTop': '50px', 'marginBottom': '50px'},
        )
    elif category == "Skills":
        fig = sparkline_figure(php_daily, selected_patient_id, 'skills')
        wordcloud_img_path = wordcloud_figure(php_daily, selected_patient_id, 'skill')
        wordcloud_component = html.Div(
            [
                html.H4("Patient's skills keywords:", className="text-white text-center",
                        style={'marginBottom': '50px'}),
                html.Img(src=wordcloud_img_path, style={'maxWidth': '80%', 'margin': '0 auto', 'display': 'block'}),
            ],
            style={'textAlign': 'center', 'marginTop': '50px', 'marginBottom': '50px'},
        )
    elif category == "Craving":
        fig = craving_line_chart(php_daily, selected_patient_id)
        wordcloud_component = html.Div()  # no wordcloud for cravings
    else:
        # Fallback to moods if unexpected input occurs
        fig = sparkline_figure(php_daily, selected_patient_id, 'moods')
        wordcloud_img_path = wordcloud_figure(php_daily, selected_patient_id)
        wordcloud_component = html.Div(
            [
                html.H4("Patient's common words:", className="text-white text-center", style={'marginBottom': '50px'}),
                html.Img(src=wordcloud_img_path, style={'maxWidth': '80%', 'margin': '0 auto', 'display': 'block'}),
            ],
            style={'textAlign': 'center', 'marginTop': '50px', 'marginBottom': '50px'},
        )

    assessment_graph = dcc.Graph(figure=fig)
    return assessment_graph, wordcloud_component


# Run the app
if __name__ == "__main__":
    app.run(debug=True)
