import pandas as pd
import numpy as np
import plotly.graph_objects as go


def spider(
    df, assessment_totals, cat_names, patient_id, title
):

    fig = go.Figure()
    fig.add_trace(
        go.Scatterpolar(
            r=df.mean()/assessment_totals,
            theta=cat_names,
            fill="toself",
            # line_color = ,
            name='Average Scores',
            hovertext=np.round(
                df.mean().values.reshape(
                    -1,
                ),
                1,
            ),
            hoverinfo="text",
        )
    )
    fig.add_trace(
        go.Scatterpolar(
            r=df.loc[patient_id]/assessment_totals,
            theta=cat_names,
            fill="toself",
            # line_color = ,
            name='Patient: ' + patient_id,
            hovertext=np.round(
                df.loc[patient_id].values.reshape(
                    -1,
                ),
                1,
            ),
            hoverinfo="text",
        )
    )

    fig.update_layout(
        title = title,
        polar=dict(radialaxis=dict(visible=False, range=[0, 1])),
        showlegend=True,
        legend=dict(
            orientation="v", font_size=12
            , yanchor="top", xanchor="left"
        )
    )

    return fig
