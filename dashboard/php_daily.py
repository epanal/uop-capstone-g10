import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from wordcloud import WordCloud
import io
import base64
from io import BytesIO
import random

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


# Function to generate the figure for PHP Dailys
def mood_sparklines(df_php_assessments, selected_patient_id):
    emotions = ["Pain", "Sad", "Anger", "Shame", "Content", "Fear", "Joy", "Anxiety", "Depressed", "Alone"]

    # Filter df for selected patient
    df_patient = df_php_assessments[df_php_assessments["group_identifier"] == selected_patient_id].copy()
    df_patient["assessment_date"] = pd.to_datetime(df_patient["assessment_date"], format="%m/%d/%Y")

    # Number of columns and rows 
    num_cols = 5  
    num_rows = 2  

    # Subplots with a grid layout
    fig = make_subplots(
        rows=num_rows, cols=num_cols, shared_xaxes=True,
        subplot_titles=[f"{emotion}" for emotion in emotions],
        vertical_spacing=0.05,  
        horizontal_spacing=0.02  
    )

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#1E1E1E",
        plot_bgcolor="#1E1E1E",
        font=dict(family="'Inter', sans-serif", size=12, color="#FFFFFF"),
        title_font=dict(family="'Inter', sans-serif", size=16, color="#FFFFFF"),
        xaxis=dict(tickfont=dict(color="#FFFFFF")),
        yaxis=dict(tickfont=dict(color="#FFFFFF"), range=[0, 5]),
        legend=dict(font=dict(color="#FFFFFF"))
    )

    # y-axis range for all subplots
    y_axis_range = [-0.1, 1.1]

    # Loop through each emotion and add a trace in the grid layout
    for i, emotion in enumerate(emotions):
        row = i // num_cols + 1  
        col = i % num_cols + 1  

        fig.add_trace(
            go.Scatter(
                x=df_patient["assessment_date"], 
                y=df_patient[emotion].astype(int),  # Convert True/False to 1/0
                mode="lines",
                name=emotion,
                line=dict(width=2),  # Make line a bit thicker for better visibility
                marker=dict(size=5),  # Increase marker size
            ),
            row=row, col=col
        )

        # Y-axis labels only for the first subplot (leftmost)
        if col == 1:
            fig.update_yaxes(
                tickvals=[0, 1], ticktext=["Not Mentioned", "Mentioned"], row=row, col=col,
                range=y_axis_range  # Ensure consistent y-axis range for all plots
            )
        else:
            # Hide the y-axis labels for other subplots
            fig.update_yaxes(showticklabels=False, row=row, col=col, 
                             range=y_axis_range)

        fig.update_xaxes(
            tickangle=45,  
            tickfont=dict(size=12),  # font size of tick labels
            row=row, col=col
        )

    fig.update_layout(
        title=f"Emotions Mentioned Over Time for Patient {selected_patient_id}",
        height=600,  # Make the chart taller
        showlegend=False,
        title_x=0.5,
        font=dict(size=14),  # Increase font size for all labels and titles
    )

    return fig

def wordcloud_figure(df_php_assessments, selected_patient_id):
    df_selected = df_php_assessments[df_php_assessments["group_identifier"] == selected_patient_id]

    # Drop NaN 
    df_selected = df_selected.dropna(subset=["Matched Words"])

    # Convert to string and join words
    matched_words = ' '.join(df_selected["Matched Words"].astype(str).tolist())

    # Generate the WordCloud
    wordcloud = WordCloud(
        width=400, height=200, background_color="#1E1E1E",
        color_func=color_func
    ).generate(matched_words)

    img = BytesIO()
    wordcloud.to_image().save(img, format='PNG')
    img.seek(0)
    wordcloud_base64 = base64.b64encode(img.read()).decode()

    return f"data:image/png;base64,{wordcloud_base64}"