import plotly.graph_objects as go
import plotly.express as px
import pandas as pd


def time_series(df, assessment, patient_id):
    """
    Args:
        df (DataFrame): The dataset containing patient assessment data.
        assessment (str): The name of the assessment to visualize.
        patient_id (str): The ID of the patient to filter data for.

    Returns:
        fig (Figure): A Plotly figure object representing the line chart with OLS regression.
    """
    # Filter data for the selected assessment and patient
    filtered_df = df[
        (df["initial_group_identifier"] == patient_id) & (df[assessment].notna())
    ]

    # Create the figure
    fig = go.Figure()

    # Add the line chart with markers
    fig.add_trace(
        go.Scatter(
            x=filtered_df["assessment_date"],
            y=filtered_df[assessment],
            mode="lines+markers",
            name=f"{assessment} Scores",
            line=dict(color="blue", width=2),
            marker=dict(size=8, color="red", symbol="circle"),
        )
    )

    # Add an OLS regression trendline using plotly.express
    if len(filtered_df) > 1:  # Ensure there are enough points for regression
        reg_fig = px.scatter(
            filtered_df,
            x="assessment_date",
            y=assessment,
            trendline="ols",
            trendline_color_override="green",
        )

        # Extract regression trace from px.scatter and add it to the main figure
        for trace in reg_fig.data:
            if trace.mode == "lines":
                fig.add_trace(
                    go.Scatter(
                        x=trace.x,
                        y=trace.y,
                        mode="lines",
                        name="Trendline (OLS Regression)",
                        line=dict(color="green", dash="dash"),
                    )
                )

    # Update layout for better aesthetics
    fig.update_layout(
        title=f"Total {assessment} Scores Over Time for Patient: {patient_id}",
        xaxis_title="Assessment Date",
        yaxis_title=f"Total {assessment} Score",
        template="plotly_dark",
        xaxis=dict(showgrid=True, gridcolor="gray", tickangle=45),
        yaxis=dict(showgrid=True, gridcolor="gray"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=40, t=40, b=40),
    )

    return fig
