import pandas as pd
import numpy as np
import plotly.graph_objects as go


def spider(
    df, assessment_totals, cat_names, patient_id, title
):

    """
    Function to create a radar chart of assessment scores for a single patient

    Args:
        df (dataframe): A dataframe of average scores for each assessment for each patient
        assessment_totals (list): A list of total possible scores for each assessment
        cat_names (list): A list of the names of each assessment, should match the order and names of
                            the columns in the dataframe, and match the order of the assessment_totals
        patient_id (string): The target patient for the plot
        title (string): The title for the plot

    Returns:
        fig (graph object): A spider chart of patient assessment scores
    """
    
    # Initialize graph object
    fig = go.Figure()
    
    # Add trace for the average assessment scores
    fig.add_trace(
        go.Scatterpolar(
            # Use normalized score for chart coordinates
            r=df.mean()/assessment_totals,
            theta=cat_names,
            fill="toself",
            # line_color = , -- NOTE: Change later to approved color palette
            name='Average Scores',
            # Use raw score for hover value
            hovertext=np.round(
                df.mean().values.reshape(
                    -1,
                ),
                1,
            ),
            hoverinfo="text",
        )
    )
    
    # Add trace for the single patient scores
    fig.add_trace(
        go.Scatterpolar(
            # Use normalized score for chart coordinates
            r=df.loc[patient_id]/assessment_totals,
            theta=cat_names,
            fill="toself",
            # line_color = , -- NOTE: Change later to approved color palette
            name='Patient: ' + patient_id,
            # Use raw score for hover value
            hovertext=np.round(
                df.loc[patient_id].values.reshape(
                    -1,
                ),
                1,
            ),
            hoverinfo="text",
        )
    )
    
    # Chart labels
    fig.update_layout(
        title=title,
        polar=dict(radialaxis=dict(visible=False, range=[0, 1])),
        showlegend=True,
        legend=dict(
            orientation="v", font_size=12
            , yanchor="top", xanchor="left"
        )
    )

    return fig
