import pandas as pd
import numpy as np
import plotly.graph_objects as go


def time_series(df, assessment, patient_id):

    df = df[df[assessment].notna()]
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df[df.initial_group_identifier == patient_id]['assessment_date'],
            y=df[df.initial_group_identifier == patient_id][assessment],
            mode='lines+markers',
            name=assessment
        )
    )

    fig.update_layout(
        title='Total ' + assessment + ' Scores Over Time for Patient: ' + patient_id,
        xaxis_title='Date',
        yaxis_title='Total ' + assessment + ' Score'
    )

    return fig
