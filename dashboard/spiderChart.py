import pandas as pd
import numpy as np
import plotly.graph_objects as go


def spider(df, assessment_totals, cat_names, patient_id, title):
    """
    Function to create a radar chart of assessment scores for a single patient.

    Args:
        df (DataFrame): A dataframe of average scores for each assessment for each patient.
        assessment_totals (list): A list of total possible scores for each assessment.
        cat_names (list): A list of the names of each assessment.
        patient_id (str): The target patient for the plot.
        title (str): The title for the plot.

    Returns:
        fig (plotly.graph_objects.Figure): A spider chart of patient assessment scores.
    """
    # Align df with cat_names to ensure matching lengths
    df = df[cat_names]

    # Add first value to end to complete circular chart
    normalized_avg_scores = (df.mean() / assessment_totals).tolist()
    normalized_avg_scores.append(normalized_avg_scores[0])

    normalized_patient_scores = (df.loc[patient_id] / assessment_totals).tolist()
    normalized_patient_scores.append(normalized_patient_scores[0])

    categories = cat_names + [cat_names[0]]  # Repeat first category at end

    # Initialize graph object
    fig = go.Figure()

    # Add trace for average assessment scores
    fig.add_trace(
        go.Scatterpolar(
            r=normalized_avg_scores,
            theta=categories,
            fill="toself",
            name="Average Scores",
            hoverinfo="r+theta",
        )
    )

    # Add trace for single patient scores
    fig.add_trace(
        go.Scatterpolar(
            r=normalized_patient_scores,
            theta=categories,
            fill="toself",
            name=f"Patient: {patient_id}",
            hoverinfo="r+theta",
        )
    )

    # Chart labels and layout
    fig.update_layout(
        title=title,
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        showlegend=True,
        legend=dict(orientation="v", font_size=12, yanchor="top", xanchor="left"),
        template="plotly_dark",
    )

    return fig
