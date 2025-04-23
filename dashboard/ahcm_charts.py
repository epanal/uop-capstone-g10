import plotly.express as px
import pandas as pd
from dash import html, dash_table

# Mapping for user-friendly display names
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

# Horizontal barplot for AHCM
def generate_ahcm_barplot(column, label, df):
    valid_data = df[column].dropna()
    value_counts = valid_data.value_counts().sort_values()

    fig = px.bar(
        x=value_counts.values,
        y=value_counts.index,
        orientation='h',
        labels={"x": "Number of Patients", "y": label},
        title=f"Distribution of {label}"
    )

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="'Inter', sans-serif", size=18, color="#FFFFFF"),
        title_font=dict(family="'Inter', sans-serif", size=26, color="#FFFFFF"),
        xaxis=dict(tickfont=dict(color="#FFFFFF")),
        yaxis=dict(tickfont=dict(color="#FFFFFF")),
        margin=dict(l=100, r=30, t=50, b=30)
    )

    return fig


def generate_patient_summary_table(df, group_identifier):
    row = df[df['group_identifier'] == group_identifier].squeeze()

    category_mapping = {
        "Physical Health": ["exercise_days_per_week", "exercise_minutes_per_day"],
        "Mental Health": ["mental_health_score", "cognitive_difficulty", "errand_difficulty", "current_stress"],
        "Substance Use": ["tobacco_use", "prescription_misuse", "illegal_drug_use_count"],
        "Basic Needs": ["financial_strain", "living_situation", "housing_problems", "food_insecurity_and_transport_issues", "utility_shutoff_threat"],
        "Safety": ["abuse_physical", "abuse_verbal", "abuse_threats", "abuse_yelling"],
        "Social Support": ["non_english_at_home", "feel_lonely", "need_daily_help", "want_work_help", "want_school_help"],
    }

    table_data = []
    for category, fields in category_mapping.items():
        for field in fields:
            response = row.get(field, "N/A")
            display_name = ahcm_column_display_names.get(field, field.replace("_", " ").title())
            table_data.append({
                "Category": category,
                "Field": display_name,
                "Response": response if pd.notna(response) else "N/A"
            })

    return dash_table.DataTable(
        data=table_data,
        columns=[
            {"name": "Category", "id": "Category"},
            {"name": "Field", "id": "Field"},
            {"name": "Response", "id": "Response"}
        ],
        style_cell={
            'textAlign': 'left',
            'padding': '10px',
            'whiteSpace': 'normal',
            'height': 'auto',
            'fontFamily': 'Arial',
            'backgroundColor': '#000000',
            'color': '#FFFFFF'
        },
        style_header={
            'backgroundColor': '#222222',
            'color': 'white',
            'fontWeight': 'bold',
            'fontSize': '16px'
        },
        style_data_conditional=[
            {'if': {'filter_query': '{Category} = "Physical Health"'}, 'backgroundColor': '#AEDFF7', 'color': 'black'},
            {'if': {'filter_query': '{Category} = "Mental Health"'}, 'backgroundColor': '#FFE0B2', 'color': 'black'},
            {'if': {'filter_query': '{Category} = "Substance Use"'}, 'backgroundColor': '#F8BBD0', 'color': 'black'},
            {'if': {'filter_query': '{Category} = "Basic Needs"'}, 'backgroundColor': '#C8E6C9', 'color': 'black'},
            {'if': {'filter_query': '{Category} = "Safety"'}, 'backgroundColor': '#FFF9C4', 'color': 'black'},
            {'if': {'filter_query': '{Category} = "Social Support"'}, 'backgroundColor': '#B3E5FC', 'color': 'black'},
            {
                'if': {'state': 'active'},
                'backgroundColor': '#D3D3D3',
                'color': 'black',
                'border': '1px solid #666'
            }
        ],
        style_table={'overflowX': 'auto'},
        page_size=len(table_data)
    )
