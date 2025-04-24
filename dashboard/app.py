from dash import Dash, html, State, dash_table, dcc, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from spiderChart import spider
from lineChart import time_series
from wordCloud import generate_wordcloud
from boxPlot import box_plot
from bps_charts import generate_bps_figure, generate_sunburst_chart
from php_daily import sparkline_figure, wordcloud_figure, craving_line_chart
from assessmentThresholds import assessment_thresholds
from ahcm_charts import generate_ahcm_barplot, generate_patient_summary_table
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
    df = df.sort_values(['group_identifier', 'assessment_date'])
    # Round assessment date to the day
    df['assessment_date'] = df['assessment_date'].dt.round('d')
    # Drop extra rows from days patients did multiple assessments
    df = df.drop_duplicates(subset=['group_identifier', 'assessment_date'], keep='last')
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
stat_tests_data = pd.read_csv(os.path.join(data_directory, 'stat_tests_data.csv'))
ahcm_df = pd.read_csv(os.path.join(data_directory, "ahcm_survey_output.csv"))

# Unique patient IDs
ahcm_ids = ahcm_df['group_identifier'].unique()

# Map for user-friendly ahcm column names
ahcm_column_display_names = {
    "living_situation" : "Living Situation",
    "housing_problems" : "Housing Problems",
    "food_insecurity_and_transport_issues" : "Food Insecurity or Transportation Issues",
    "want_work_help" : "Want Work Help",
    "need_daily_help" : "Need Daily Help",
    "feel_lonely" : "Feel Lonely",
    "non_english_at_home" : "English Not Spoken at Home",
    "want_school_help" : "Want School Help",
    "tobacco_use" : "Tobacco Use",
    "illegal_drug_use_count" : "Illegal Drug Use",
    "exercise_days_per_week": "Exercise Days per Week",
    "exercise_minutes_per_day": "Exercise Minutes per Day",
    "binge_drinking": "Binge Drinking Frequency",
    "mental_health_score": "Mental Health Score",
    "prescription_misuse" : "Prescription Misuse",
    "financial_strain": "Financial Strain",
    "abuse_physical": "Physical Abuse Frequency",
    "abuse_verbal": "Verbal Abuse Frequency",
    "abuse_threats": "Threats of Harm",
    "abuse_yelling": "Yelling or Screaming Frequency",
    "utility_shutoff_threat": "Utility Shutoff Threat",
    "cognitive_difficulty": "Cognitive Difficulty",
    "errand_difficulty": "Errand Difficulty",
    "current_stress": "Current Stress Level"
}

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

# welcome page plots
all_internal_motivation = " ".join(bps_df['int_motivation'].dropna())
all_external_motivation = " ".join(bps_df['ext_motivation'].dropna())
internal_wc = generate_wordcloud(all_internal_motivation, "Internal Motivation", "Blues")
external_wc = generate_wordcloud(all_external_motivation, "External Motivation", "Oranges")

# program type pie chart
program_pie = px.pie(stat_tests_data, names='program',
                     title='Program Types', hole=0.3)
program_pie.update_layout(title_text='Program Types', title_x=0.5, template="plotly_dark")
# discharge type pie chart
discharge_pie = px.pie(stat_tests_data, names='discharge_type',
                       title='Discharge Types', hole=0.3)
discharge_pie.update_layout(title_text='Discharge Types', title_x=0.5, template="plotly_dark")

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
cols = ["group_identifier", "assessment_date", "score"]
assessments = ["WHO", "GAD", "PHQ", "PCL", "DERS"]

df = who[cols].merge(
    gad[cols],
    how="outer",
    on=["group_identifier", "assessment_date"],
    suffixes=("_WHO", "_GAD"),
)
df = df.merge(
    phq[cols],
    how="outer",
    on=["group_identifier", "assessment_date"],
    suffixes=(None, "_PHQ"),
)
df = df.merge(
    pcl[cols],
    how="outer",
    on=["group_identifier", "assessment_date"],
    suffixes=(None, "_PCL"),
)
df = df.merge(
    ders[cols],
    how="outer",
    on=["group_identifier", "assessment_date"],
    suffixes=(None, "_DERS"),
)
df.columns = ["group_identifier", "assessment_date"] + assessments

scores = df.groupby("group_identifier")[assessments].mean()

# Total possible score for each assessment
totals = [25.0, 21.0, 27.0, 80.0, 180.0]

# Current date
now = datetime.now()

# Initialize the app with Bootstrap theme
app = Dash(__name__,
           #suppress_callback_exceptions=True,
            external_stylesheets=[dbc.themes.CYBORG])

# App layout with centered dropdowns and plots
app.layout = dbc.Container(
    [
        html.Br(),
        # Title Section with Logo
        html.Div(
            [
                # Logo Image
                html.Img(
                    src=app.get_asset_url("exist_logo_white.webp"),
                    style={"height": "80px", "marginBottom": "20px"}
                ),
                # Title Text
                html.H2(
                    "Patient Assessment Dashboard",
                    className="text-center text-white"
                ),
            ],
            style={"textAlign": "center", "marginTop": "20px"}
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
                    label="Welcome!",
                    tab_id="tab-0",
                    children=[
                        html.Br(),
                        html.Div(
                            [
                                html.H4("Patient Motivations",
                                        className="text-white bg-dark p-2 rounded",
                                        style={'textAlign': 'center'})
                            ], style={"width": "50%", "margin": "auto"},
                        ),
                        dbc.Row([
                            dbc.Col([
                                html.Img(src=f"data:image/png;base64,{internal_wc}",
                                         style={'width': '100%', 'height': '100%', 'borderRadius': '8px'})
                            ], width={"size": 5}, align="center"),
                            dbc.Col([
                                html.Img(src=f"data:image/png;base64,{external_wc}",
                                         style={'width': '100%', 'height': '100%', 'borderRadius': '8px'})
                            ], width={"size": 5}, align="center")
                        ], align="center", justify="center"),
                        html.Br(),
                        html.Div(
                            [
                                html.H4("Patient Distributions",
                                        className="text-white bg-dark p-2 rounded",
                                        style={'textAlign': 'center'})
                            ], style={"width": "50%", "margin": "auto"},
                        ),
                        dbc.Row([
                            dbc.Col([
                                dcc.Graph(id='program-pie', figure=program_pie)
                            ], width={"size": 5}, align="center"),
                            dbc.Col([
                                dcc.Graph(id='discharge-pie', figure=discharge_pie)
                            ], width={"size": 5}, align="center")
                        ], align="center", justify="center"),
                        html.Br(),
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
                                                        "group_identifier"
                                                    ].unique()
                                                ],
                                                value=df[
                                                    "group_identifier"
                                                ].unique()[0],
                                                clearable=False,
                                            ),
                                        ],
                                        style={"width": "50%", "margin": "auto"},
                                    ),
                                    html.Br(),
                                    html.Div(children=[
                                        html.Div(
                                            dash_table.DataTable(
                                                id='assessment-scores',
                                                data=df.to_dict('records'),
                                                columns=[
                                                    {'name': 'Initial Group Identifier'
                                                        , 'id': 'group_identifier', 'type': 'text'},
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
                                                                'filter_query': '{} <= {{{}}} < {}'.format(
                                                                    threshold_range[0], 'WHO', threshold_range[1]
                                                                ),
                                                                'column_id': 'WHO'
                                                            },
                                                            'backgroundColor': color,
                                                            'color': 'black'
                                                        } for threshold_range, color in zip(
                                                                assessment_thresholds['WHO']['ranges'],
                                                                assessment_thresholds['WHO']['colors']
                                                            )
                                                    ] +
                                                    [
                                                        {
                                                            'if': {
                                                                'filter_query': '{} <= {{{}}} < {}'.format(
                                                                    threshold_range[0], 'GAD', threshold_range[1]
                                                                ),
                                                                'column_id': 'GAD'
                                                            },
                                                            'backgroundColor': color,
                                                            'color': 'black'
                                                        } for threshold_range, color in zip(
                                                                assessment_thresholds['GAD']['ranges'],
                                                                assessment_thresholds['GAD']['colors']
                                                            )
                                                    ] +
                                                    [
                                                        {
                                                            'if': {
                                                                'filter_query': '{} <= {{{}}} < {}'.format(
                                                                    threshold_range[0], 'PHQ', threshold_range[1]
                                                                ),
                                                                'column_id': 'PHQ'
                                                            },
                                                            'backgroundColor': color,
                                                            'color': 'black'
                                                        } for threshold_range, color in zip(
                                                                assessment_thresholds['PHQ']['ranges'],
                                                                assessment_thresholds['PHQ']['colors']
                                                            )
                                                    ] +
                                                    [
                                                        {
                                                            'if': {
                                                                'filter_query': '{} <= {{{}}} < {}'.format(
                                                                    threshold_range[0], 'PCL', threshold_range[1]
                                                                ),
                                                                'column_id': 'PCL'
                                                            },
                                                            'backgroundColor': color,
                                                            'color': 'black'
                                                        } for threshold_range, color in zip(
                                                                assessment_thresholds['PCL']['ranges'],
                                                                assessment_thresholds['PCL']['colors']
                                                            )
                                                    ] +
                                                    [
                                                        {
                                                            'if': {
                                                                'filter_query': '{} <= {{{}}} < {}'.format(
                                                                    threshold_range[0], 'DERS', threshold_range[1]
                                                                ),
                                                                'column_id': 'DERS'
                                                            },
                                                            'backgroundColor': color,
                                                            'color': 'black'
                                                        } for threshold_range, color in zip(
                                                                assessment_thresholds['DERS']['ranges'],
                                                                assessment_thresholds['DERS']['colors']
                                                            )
                                                    ] +
                                                    [
                                                        {
                                                            'if': {
                                                                'filter_query': '{{{}}} is nil'.format(col),
                                                                'column_id': col
                                                            },
                                                            'backgroundColor': 'rgb(50, 50, 50)'
                                                        } for col in assessment_thresholds.keys()
                                                    ]
                                                )
                                            )
                                        ),

                                    ], style={"width": "50%", "margin": "auto"}),
                                ],
                                width=12,
                            ),
                        ),
                        html.Br(),
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
                                    html.Br(),
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
                        html.Br(),
                    ],
                ),
                # Assessment Scores by Program and Discharge type
                dbc.Tab(
                    label= "📦 Box-Plots",
                    tab_id="tab-6",
                    children=[
                        html.Br(),
                        dbc.Row(
                            dbc.Col(
                                [
                                    html.Div(
                                        [
                                            html.Label(
                                                "Select Assessment:",
                                                className="text-white",
                                            ),
                                            dcc.Dropdown(
                                                id="box-assessment-select",
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
                                ], width=12,
                            )
                        ),
                        html.Br(),
                        dbc.Row([
                            dbc.Col([
                                dcc.Graph(id='program-box-plot',style={'width': '90%', 'height': '60%'})
                            ], width={"size": 5}),
                            dbc.Col([
                                dcc.Graph(id='discharge-box-plot',style={'width': '90%', 'height': '60%'})
                            ], width={"size": 5})
                        ], align="center", justify="center"),
                        html.Br(),
                    ],
                ),
                # Line Chart Tab
                dbc.Tab(
                    label="📈 Risk Analysis",
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
                                                        "group_identifier"
                                                    ].unique()
                                                ],
                                                value=df[
                                                    "group_identifier"
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
                                        [
                                            html.Label(
                                                "Adjust Standard Deviation Threshold:",
                                                className="text-white",
                                            ),
                                            dcc.Slider(
                                                id="std-threshold-slider",
                                                min=0.5,
                                                max=3.0,
                                                step=0.1,
                                                value=1.5,
                                                marks={i: str(i) for i in range(1, 4)},
                                                tooltip={
                                                    "always_visible": True,
                                                    "placement": "bottom",
                                                },
                                            ),
                                        ],
                                        style={
                                            "width": "50%",
                                            "margin": "auto",
                                            "padding-top": "10px",
                                            "padding-bottom": "20px",
                                        },
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
                        html.Br(),
                    ],
                ),
                # Biopsychosocial Assessment Tab with Toggle
                dbc.Tab(
                    label="🏥 Biopsychosocial Assessment",
                    tab_id="tab-4",
                    children=[
                        html.Br(),
                        # Radio button to choose view mode
                        dbc.Row(
                            dbc.Col(
                                dcc.RadioItems(
                                    id="bps-view-selection",
                                    options=[
                                        {"label": "All Patients", "value": "all"},
                                        {"label": "Individual Patient", "value": "select"}
                                    ],
                                    value="all",  # Default to All Patients view
                                    labelStyle={'display': 'inline-block', 'margin-right': '20px', 'fontSize': '20px'},
                                    inputStyle={"margin-right": "10px"}
                                ),
                                width=6,
                                className="mx-auto",
                            ),
                            style={"textAlign": "center"}
                        ),
                        html.Br(),
                        # Container for All Patients view (sunburst chart)
                        html.Div(
                            id="bps-all-container",
                            children=[
                                dbc.Row(
                                    dbc.Col(
                                        dcc.Graph(
                                            id="sunburst-chart",
                                            figure=sunburst_fig,
                                            style={"height": "70vh", "width": "100%"}
                                        ),
                                        width=6,
                                        className="mx-auto"
                                    )
                                )
                            ]
                        ),
                        # Container for Select Patient view
                        html.Div(
                            id="bps-select-container",
                            children=[
                                dbc.Row(
                                    dbc.Col(
                                        html.Div(
                                            [
                                                html.Label("Select Patient:", className="text-white"),
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
                                            style={"width": "100%"}
                                        ),
                                        width=6,
                                        className="mx-auto"
                                    )
                                ),
                                html.Br(),
                                dbc.Row(
                                    dbc.Col(
                                        html.Div(
                                            id="bps-content",
                                            style={"width": "100%"}
                                        ),
                                        width=6,
                                        className="mx-auto"
                                    )
                                ),
                                html.Br(),
                            ]
                        ),
                    ]
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
                                                labelStyle={'display': 'inline-block', 'margin-right': '20px', 'fontSize': '20px'},
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
                # AHCM Assessment Layout
                dbc.Tab(
                    label="📉 AHCM Assessment",
                    tab_id="tab-ahcm-assessment",
                    children=[
                        html.Br(),
                        dbc.Row(
                            dbc.Col(
                                dcc.RadioItems(
                                    id="ahcm-view-selection",
                                    options=[
                                        {"label": "All Patients", "value": "all"},
                                        {"label": "Individual Patient", "value": "select"}
                                    ],
                                    value="all",
                                    labelStyle={'display': 'inline-block', 'margin-right': '20px', 'fontSize': '20px'},
                                    inputStyle={"margin-right": "10px"}
                                ),
                                width=6,
                                className="mx-auto",
                            ),
                            style={"textAlign": "center"}
                        ),
                        html.Br(),
                        html.Div(id="ahcm-all-container", children=[
                            dbc.Row([
                                dbc.Col([
                                    html.Div([
                                        html.Label("Select Column:", className="text-white"),
                                        dcc.Dropdown(
                                            id="ahcm-feature-dropdown",
                                            options=[
                                                {"label": ahcm_column_display_names.get(col, col), "value": col}
                                                for col in ahcm_df.columns if col != 'group_identifier'
                                            ],
                                            value=[col for col in ahcm_df.columns if col != 'group_identifier'][0],
                                            clearable=False,
                                        )
                                    ], style={"width": "50%", "margin": "auto"}),
                                    html.Br(),
                                    html.Div(
                                        dcc.Graph(id='ahcm-barplot'),
                                        style={"width": "60%", "margin": "auto"}  # 👈 Adjust width here
                                    )
                                ], width=12)
                            ])
                        ]),
                    html.Div(id="ahcm-select-container", children=[
                        dbc.Row([
                            dbc.Col([
                                html.Div([
                                    html.Label("Select Patient:", className="text-white"),
                                    dcc.Dropdown(
                                        id="ahcm-patient-dropdown",
                                        options=[{"label": pid, "value": pid} for pid in ahcm_ids],
                                        value=ahcm_ids[0],
                                        clearable=False,
                                    )
                                ], style={"width": "50%", "margin": "auto"})  # 👈 wrap both inside here
                            ])
                        ]),
                        html.Br(),
                        dbc.Row([
                            dbc.Col([
                                html.Div(id='ahcm-patient-details', style={'color': 'white', 'padding': '20px'})
                            ], width=8, className="mx-auto")
                        ])
                    ])
                    ]
                )
            ],
            style={
                "fontSize": "20px",        # Increase font size
                "padding": "12px 20px",     # Increase padding
                "margin": "0 5px"
            },
        ),
    ],
    fluid=True,
)


# Callbacks for Assessment Scores Table
@app.callback(
    Output("assessment-scores", "data"),
    [Input("assessment-table-patient-select", "value")],
)
def update_data_table(patient_id):
    table_data = df.copy()
    table_data['assessment_date'] = table_data['assessment_date'].dt.strftime('%Y-%m-%d')
    return table_data[table_data.group_identifier == patient_id].to_dict('records')


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
    [
        Input("line-patient-select", "value"),
        Input("line-assessment-select", "value"),
        Input("std-threshold-slider", "value"),
    ],
)
def update_line_chart(patient_id, assessment, std_threshold):
    return time_series(df, assessment, patient_id, std_threshold)

@app.callback(
    [Output("bps-all-container", "style"),
     Output("bps-select-container", "style")],
    [Input("bps-view-selection", "value")]
)
def update_bps_view(view_selection):
    if view_selection == "all":
        return {"display": "block"}, {"display": "none"}
    else:
        return {"display": "none"}, {"display": "block"}

# Callback for BPS Chart (Select Patient view)
@app.callback(
    Output('bps-content', 'children'),
    [Input('bps-patient-dropdown', 'value')]
)
def update_bps_content(patient_id):
    # Filter the patient data for BPS
    filtered_df = bps_df[bps_df['group_identifier'] == patient_id]
    patient_info = filtered_df[['group_identifier', 'age', 'int_motivation', 'ext_motivation']].drop_duplicates().iloc[0]

    # Biopsychosocial aggregate and individual scores
    bps_cols = [col for col in bps_column_mapping.values() if col != "Total"]
    bps_aggregates = bps_df[bps_cols].agg(['mean', 'median']).transpose()
    individual_scores = filtered_df[bps_cols].iloc[0]
    patient_ban = filtered_df[bps_cols].sum(axis=1).iloc[0]
    total_bps_avg = bps_df[bps_cols].sum(axis=1).mean()

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
                'overflowX': 'auto',
                'marginTop': '20px',
            },
            style_cell={
                'textAlign': 'left',
                'color': 'white',
                'backgroundColor': '#1a1a1a',
                'padding': '5px',
            },
            style_header={
                'backgroundColor': '#343a40',
                'fontWeight': 'bold',
                'color': 'white',
            },
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': '#212529',
                }
            ],
            sort_action='native',  # Enable sorting
        )
    else:
        sub_history_table = html.P("No substance use history (use_flag=1) available for this patient.",
                                   className="text-white")

    return html.Div([
        html.H4("Patient Overview", className="text-white bg-dark p-2 rounded", style={'textAlign': 'center'}),
        html.P(f"Patient ID: {patient_info['group_identifier']}", className="text-white"),
        html.P(f"Age: {patient_info['age']}", className="text-white"),
        html.P(f"Internal Motivation: {patient_info['int_motivation']}", className="text-white"),
        html.P(f"External Motivation: {patient_info['ext_motivation']}", className="text-white"),
        html.H4("Substance Use History", className="text-white bg-dark p-2 rounded mt-4",
                style={'textAlign': 'center'}),
        sub_history_table,
        html.H4("Biopsychosocial Scores", className="text-white bg-dark p-2 rounded mt-4",
                style={'textAlign': 'center'}),
        html.Div([
            html.Span(f"Patient's Total: {round(patient_ban, 2)}", style={'color': '#FF5722', 'margin-right': '20px'}),
            html.Span(f"Average Total (All Patients): {round(total_bps_avg, 1)}", style={'color': '#00BCD4'})
        ], className="mb-3"),
        dcc.Graph(figure=fig)
    ],
    style={"fontSize": "18px"})


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
                html.H4("Patient's common moods:", className="text-white bg-dark p-2 rounded",
                        style={'textAlign': 'center'}),
                html.Img(src=wordcloud_img_path, style={'maxWidth': '80%', 'margin': '0 auto', 'display': 'block'}),
            ],
            style={"width": "50%", "margin": "auto"},
        )
    elif category == "Supports":
        fig = sparkline_figure(php_daily, selected_patient_id, 'supports')
        wordcloud_img_path = wordcloud_figure(php_daily, selected_patient_id, 'support')
        wordcloud_component = html.Div(
            [
                html.H4("Patient's support keywords:", className="text-white bg-dark p-2 rounded",
                        style={'textAlign': 'center'}),
                html.Img(src=wordcloud_img_path, style={'maxWidth': '80%', 'margin': '0 auto', 'display': 'block'}),
            ],
            style={"width": "50%", "margin": "auto"},
        )
    elif category == "Skills":
        fig = sparkline_figure(php_daily, selected_patient_id, 'skills')
        wordcloud_img_path = wordcloud_figure(php_daily, selected_patient_id, 'skill')
        wordcloud_component = html.Div(
            [
                html.H4("Patient's skills keywords:", className="text-white bg-dark p-2 rounded",
                        style={'textAlign': 'center'}),
                html.Img(src=wordcloud_img_path, style={'maxWidth': '80%', 'margin': '0 auto', 'display': 'block'}),
            ],
            style={"width": "50%", "margin": "auto"},
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
                html.H4("Patient's common words:", className="text-white bg-dark p-2 rounded",
                        style={'textAlign': 'center'}),
                html.Img(src=wordcloud_img_path, style={'maxWidth': '80%', 'margin': '0 auto', 'display': 'block'}),
            ],
            style={"width": "50%", "margin": "auto"},
        )

    assessment_graph = dcc.Graph(figure=fig)
    return assessment_graph, wordcloud_component


# Callbacks for Box Plot
@app.callback(
    Output("program-box-plot", "figure"),
    [Input("box-assessment-select", "value")],
)
def update_program_box_plot(assessment):
    return box_plot(stat_tests_data, 'program', assessment)


# Callbacks for Box Plot
@app.callback(
    Output("discharge-box-plot", "figure"),
    [Input("box-assessment-select", "value")],
)
def update_discharge_box_plot(assessment):
    return box_plot(stat_tests_data, 'discharge_type', assessment)

# Callbacks for AHCM 
@app.callback(
    [Output("ahcm-all-container", "style"), Output("ahcm-select-container", "style")],
    [Input("ahcm-view-selection", "value")]
)
def toggle_ahcm_view(view):
    if view == "all":
        return {"display": "block"}, {"display": "none"}
    else:
        return {"display": "none"}, {"display": "block"}

@app.callback(
    Output("ahcm-barplot", "figure"),
    Input("ahcm-feature-dropdown", "value")
)
def update_ahcm_barplot(feature):
    label = ahcm_column_display_names.get(feature, feature)
    return generate_ahcm_barplot(feature, label, ahcm_df)

@app.callback(
    Output("ahcm-patient-details", "children"),
    Input("ahcm-patient-dropdown", "value")
)
def update_ahcm_patient_summary(pid):
    return generate_patient_summary_table(ahcm_df, pid)




# Run the app
if __name__ == "__main__":
    app.run(debug=True)
