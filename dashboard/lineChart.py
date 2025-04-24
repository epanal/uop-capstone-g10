import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from assessmentThresholds import assessment_thresholds


def time_series(df, assessment, patient_id, std_threshold=1.5):
    """
    Args:
        df (DataFrame): The dataset containing patient assessment data.
        assessment (str): The name of the assessment to visualize.
        patient_id (str): The ID of the patient to filter data for.
        std_threshold (float): Number of standard deviations for outlier detection.

    Returns:
        fig (Figure): Enhanced line chart with multiple features.
    """
    # Filter data for the selected assessment and patient
    filtered_df = df[
        (df["group_identifier"] == patient_id) & (df[assessment].notna())
    ].sort_values("assessment_date")

    # Calculate statistics
    mean_score = filtered_df[assessment].mean()
    std_score = filtered_df[assessment].std()
    upper_bound = mean_score + std_threshold * std_score
    lower_bound = mean_score - std_threshold * std_score

    # Identify outliers
    filtered_df["is_outlier"] = np.where(
        (filtered_df[assessment] > upper_bound)
        | (filtered_df[assessment] < lower_bound),
        True,
        False,
    )

    # Calculate percentage change for insights
    if len(filtered_df) > 1:
        first_score = filtered_df[assessment].iloc[0]
        last_score = filtered_df[assessment].iloc[-1]
        percent_change = (
            ((last_score - first_score) / first_score) * 100 if first_score != 0 else 0
        )
    else:
        percent_change = 0

    # Create the figure
    fig = go.Figure()

    # Add filled area under the curve
    fig.add_trace(
        go.Scatter(
            x=filtered_df["assessment_date"],
            y=filtered_df[assessment],
            mode="lines",
            line=dict(color="royalblue", width=3),
            fill="tozeroy",
            fillcolor="rgba(100, 150, 255, 0.2)",
            name=f"Trend",
        )
    )

    # Add color-mapped markers with size variation
    fig.add_trace(
        go.Scatter(
            x=filtered_df["assessment_date"],
            y=filtered_df[assessment],
            mode="markers",
            marker=dict(
                size=12,
                color=filtered_df[assessment],
                line=dict(width=2, color="DarkSlateGrey"),
            ),
            name=f"Assessment Scores",
            hovertemplate="<b>Date:</b> %{x}<br><b>Score:</b> %{y}<extra></extra>",
        )
    )

    # Highlight outliers with different markers
    outliers = filtered_df[filtered_df["is_outlier"]]
    if not outliers.empty:
        fig.add_trace(
            go.Scatter(
                x=outliers["assessment_date"],
                y=outliers[assessment],
                mode="markers",
                marker=dict(
                    size=16,
                    color="crimson",
                    symbol="triangle-up",
                    line=dict(width=2, color="black"),
                ),
                name="Notable Scores",
                hovertemplate="<b>Date:</b> %{x}<br><b>Score:</b> %{y}<br><b>Note:</b> This score is significantly different from typical patterns<extra></extra>",
            )
        )

    # Add standard deviation boundaries
    fig.add_hline(
        y=upper_bound,
        line=dict(color="white", dash="dot", width=4),
        annotation_text="Above Usual Range",
        annotation_position="bottom right",
    )

    fig.add_hline(
        y=lower_bound,
        line=dict(color="white", dash="dot", width=4),
        annotation_text="Below Usual Range",
        annotation_position="top right",
    )

    # Get thresholds for the selected assessment
    thresholds = assessment_thresholds.get(assessment)

    # Add threshold rectangles based on the selected assessment
    if thresholds:
        for i, ((y0, y1), label, color) in enumerate(
            zip(thresholds["ranges"], thresholds["labels"], thresholds["colors"])
        ):
            fig.add_hrect(
                y0=y0,
                y1=y1,
                fillcolor=color,
                layer="below",
                line_width=0,
                annotation_text=label,
                annotation_position="left",
            )

    # Add OLS trendline
    if len(filtered_df) > 1:
        reg_fig = px.scatter(
            filtered_df,
            x="assessment_date",
            y=assessment,
            trendline="ols",
            trendline_color_override="green",
        )

        for trace in reg_fig.data:
            if trace.mode == "lines":
                fig.add_trace(
                    trace.update(name="Overall Trend", line=dict(dash="dash", width=2))
                )

    # Update layout
    fig.update_layout(
        title=f"{assessment} Scores for Patient {patient_id}",
        xaxis_title="Assessment Date",
        yaxis_title="Score Value",
        template="plotly_dark",
        hovermode="x unified",
        xaxis=dict(
            showgrid=True,
            gridcolor="rgba(100, 100, 100, 0.3)",
            tickangle=25,
            title=dict(standoff=30),
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(100, 100, 100, 0.3)",
            range=[
                max(0, filtered_df[assessment].min() - 5),
                filtered_df[assessment].max() + 5,
            ],
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=40, t=80, b=100),  # Increased bottom margin
        height=600,
    )

    # Add key insight at the bottom of the chart
    if len(filtered_df) > 1:
        direction = "improved" if percent_change < 0 else "increased"
        fig.add_annotation(
            x=0.5,
            y=-0.1,
            xref="paper",
            yref="paper",
            text=f"<b>Key Insight:</b> Assessment scores have {direction} by {abs(round(percent_change))}% since initial assessment.",
            showarrow=False,
            font=dict(size=14),
            bgcolor="rgba(255,255,255,0.2)",
            bordercolor="#444",
            borderwidth=1,
            borderpad=4,
            xanchor="center",
            yanchor="top",
        )

    return fig
