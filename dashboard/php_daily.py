import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from wordcloud import WordCloud
import math
import io
import base64
from io import BytesIO
import random
from PIL import Image

# Define a color map for emotions
emotion_colors = {
    "Pain": "#FF5733",
    "Sad": "#3498DB",
    "Anger": "#E74C3C",
    "Shame": "#9B59B6",
    "Content": "#2ECC71",
    "Fear": "#F39C12",
    "Joy": "#F1C40F",
    "Anxiety": "#E67E22",
    "Depressed": "#34495E",
    "Alone": "#95A5A6"
}

# default white
def color_func(word, font_size, position, orientation, random_state=None, **kwargs):
    return emotion_colors.get(word, "#FFFFFF")  # Default to white if not in dictionary


def sparkline_figure(df_php_assessments, selected_patient_id, category):
    """
    Generate a sparkline figure for a given patient and category.
    
    Parameters:
      - df_php_assessments: DataFrame with PHP assessment data.
      - selected_patient_id: The patient identifier.
      - category: String indicating which category to plot. Acceptable values are
                  "Moods", "Skills", or "Supports".
                  
    Returns:
      - A Plotly Figure object containing the subplots.
    """
    # Define the column names for each category 
    categories = {
        "moods": ["Pain", "Sad", "Anger", "Shame", "Content", "Fear", "Joy", "Anxiety", "Depressed", "Alone"],
        "skills": ["Mindfulness/Meditation", "Distress Tolerance", "Opposite Action", "Take My Meds",
                   "Ask For Help", "Improve Moment", "Parts Work", "Play The Tape Thru", "Values"],
        "supports": ["Sleep", "Nutrition", "Exercise", "Fun", "Connection", "Warmth", "Water", "Love", "Therapy"]
    }
    
    # Convert category to lowercase to match dictionary keys
    cat_key = category.lower()
    if cat_key not in categories:
        # Return an empty figure if category is unrecognized
        return go.Figure()
    
    items = categories[cat_key]
    
    # Filter for the patient and ensure dates are datetime
    df_patient = df_php_assessments[df_php_assessments["group_identifier"] == selected_patient_id].copy()
    df_patient["assessment_date"] = pd.to_datetime(df_patient["assessment_date"], format="%m/%d/%Y")
    
    num_cols = 5
    num_rows = math.ceil(len(items) / num_cols)

    fig = make_subplots(
        rows=num_rows,
        cols=num_cols,
        shared_xaxes=False,
        subplot_titles=items,
        vertical_spacing=0.3, 
        horizontal_spacing=0.02
    )
    
    # y-axis range
    y_axis_range = [-0.1, 1.1]
    
    # Loop through each item and add a trace 
    for i, item in enumerate(items):
        row = i // num_cols + 1
        col = i % num_cols + 1

        # Check if the column exists in the df
        if item in df_patient.columns:
            y_values = df_patient[item].astype(int)
        else:
            y_values = [None] * len(df_patient)
        
        fig.add_trace(
            go.Scatter(
                x=df_patient["assessment_date"],
                y=y_values,
                mode="lines",
                name=item,
                line=dict(width=2),
                marker=dict(size=5)
            ),
            row=row, col=col
        )
        
        # leftmost column, show y-axis labels (0/1 as Not Mentioned / Mentioned)
        if col == 1:
            fig.update_yaxes(
                tickvals=[0, 1],
                ticktext=["Not Mentioned", "Mentioned"],
                row=row, col=col,
                range=y_axis_range,
                showticklabels=True
            )
        else:
            fig.update_yaxes(
                showticklabels=False, 
                tickfont=dict(size=12),
                row=row, col=col,
                range=y_axis_range
            )
        
        # x-axis settings
        fig.update_xaxes(
            tickangle=45,
            tickfont=dict(size=12),
            row=row, col=col,
            showticklabels=True
        )
    
    #  overall layout
    fig.update_layout(
        title=f"{category.capitalize()} Mentioned Over Time for Patient {selected_patient_id}",
        height=800,
        showlegend=False,
        title_x=0.5,
        font=dict(size=20),
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    )
    
    return fig

def craving_line_chart(df_php_assessments, selected_patient_id):
    # Filter df for the selected patient
    df_patient = df_php_assessments[df_php_assessments["group_identifier"] == selected_patient_id].copy()
    
    # Convert assessment_date to datetime
    df_patient["assessment_date"] = pd.to_datetime(df_patient["assessment_date"], format="%m/%d/%Y")
    
    fig = go.Figure(
        data=go.Scatter(
            x=df_patient["assessment_date"],
            y=df_patient["Craving"].astype(float),  # Ensure the craving is numeric
            mode="lines+markers",
            line=dict(width=2),
            marker=dict(size=6)
        )
    )
    
    # styling
    fig.update_layout(
        title=f"Craving Over Time for Patient {selected_patient_id}",
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            title="Assessment Date",
            tickangle=45,
            tickfont=dict(color="#FFFFFF")
        ),
        title_font=dict(family="'Inter', sans-serif", size=26, color="#FFFFFF"),
        yaxis=dict(
            title="Craving",
            tickfont=dict(color="#FFFFFF")
        ),
        font=dict(
            family="'Inter', sans-serif",
            size=18,
            color="#FFFFFF"
        ),
        height=600,
        showlegend=False,
        title_x=0.5
    )
    
    return fig

def wordcloud_figure(df_php_assessments, selected_patient_id, category):
    df_selected = df_php_assessments[df_php_assessments["group_identifier"] == selected_patient_id]

    # Convert to string and join words
    if category ==  'mood':
        df_selected = df_selected.dropna(subset=["Matched Emotion Words"])
        matched_words = ' '.join(df_selected["Matched Emotion Words"].astype(str).tolist())
    elif category == 'support':
        df_selected = df_selected.dropna(subset=["Match Support Words"])
        matched_words = ' '.join(df_selected["Match Support Words"].astype(str).tolist())    
    elif category == 'skill':
        df_selected = df_selected.dropna(subset=["Match Skill Words"])
        matched_words = ' '.join(df_selected["Match Skill Words"].astype(str).tolist())    
    else:
        matched_words = ""

    # Check if there are any words to display
    if not matched_words.strip():
        # Create a blank image with a dark background to serve as a placeholder
        img = Image.new('RGB', (400, 200), color=(30, 30, 30))
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img.seek(0)
        wordcloud_base64 = base64.b64encode(buffered.read()).decode()
        return f"data:image/png;base64,{wordcloud_base64}"

    # Generate WordCloud
    wordcloud = WordCloud(
        width=600, height=300, background_color='#1E1E1E',
        color_func=lambda *args, **kwargs: "#FFFFFF" 
    ).generate(matched_words)

    img = BytesIO()
    wordcloud.to_image().save(img, format='PNG')
    img.seek(0)
    wordcloud_base64 = base64.b64encode(img.read()).decode()

    return f"data:image/png;base64,{wordcloud_base64}"
