import plotly.express as px
import pandas as pd
from dash import html

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


def generate_patient_summary_card(df, group_identifier):
    row = df[df['group_identifier'] == group_identifier].squeeze()

    category_mapping = {
        "Physical Health": ["exercise_days_per_week", "exercise_minutes_per_day"],
        "Mental Health": ["mental_health_score","cognitive_difficulty", "errand_difficulty", "current_stress"],
        "Substance Use": ["tobacco_use", "prescription_misuse", "illegal_drug_use_count"],
        "Basic Needs": ["financial_strain", "living_situation", "housing_problems", "food_insecurity_and_transport_issues", "utility_shutoff_threat"],
        "Safety": ["abuse_physical", "abuse_verbal", "abuse_threats", "abuse_yelling"],
        "Social Support": ["non_english_at_home", "feel_lonely", "need_daily_help", "want_work_help", "want_school_help"],
    }

    cards = []
    for category, fields in category_mapping.items():
        items = [
            html.Li(f"{ahcm_column_display_names.get(field, field)}: {row.get(field, 'N/A') if pd.notna(row.get(field, 'N/A')) else 'N/A'}")
            for field in fields
        ]
        cards.append(html.Div([
            html.H5(category, className="text-white bg-dark p-2 rounded"),
            html.Ul(items, style={"fontSize": "18px"})
        ], style={
            'border': '1px solid #ccc',
            'padding': '15px',
            'margin': '10px',
            'borderRadius': '10px',
            'boxShadow': '0 2px 5px rgba(0,0,0,0.1)'
        }))

    return html.Div([
        html.H4("AHCM Summary", className="text-white bg-dark p-2 rounded text-center"),
        html.Div(cards, style={'display': 'flex', 'flexWrap': 'wrap'})
    ])
