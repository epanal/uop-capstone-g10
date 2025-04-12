import plotly.express as px
import pandas as pd

def generate_sunburst_chart(dataframe, total_patients):
    """
    Generates a Sunburst chart for substance use breakdown.

    Parameters:
    - dataframe: DataFrame containing the substance use data.
    - total_patients: Total number of patients, used for the chart title.

    Returns:
    - A Plotly Sunburst figure.
    """
    fig = px.sunburst(
        dataframe,
        path=['substance', 'pattern_of_use_consolidated'],
        values='count',
        title=f'Substance Use Breakdown by Pattern (Total Patients: {total_patients})'
    )

    # Assign custom data for hover information
    def assign_customdata(trace):
        customdata = []
        for i, label in enumerate(trace['labels']):
            if trace['parents'][i] == '':  # Inner circle (substance)
                substance = label
                # Sum the 'count' for all rows where substance matches
                substance_total = dataframe[dataframe['substance'] == substance]['count'].sum()
                # Calculate percentage based on total_patients
                percentage = (substance_total / total_patients) * 100
                customdata.append([percentage])
            else:  # Outer circle (pattern)
                pattern = label
                row = dataframe[
                    (dataframe['substance'] == trace['parents'][i]) & 
                    (dataframe['pattern_of_use_consolidated'] == pattern)
                ]
                percentage = row['percentage'].values[0] if not row.empty else 0
                customdata.append([percentage])
        return customdata

    fig.update_traces(
        hovertemplate=(
            '%{label}<br>'
            'Count: %{value} patients<br>'
            'Percentage: %{customdata:.1f}% of total patients<extra></extra>'
        ),
        customdata=assign_customdata(fig.data[0])
    )

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="'Inter', sans-serif", size=18, color="#FFFFFF"),
        title_font=dict(family="'Inter', sans-serif", size=26, color="#FFFFFF"),
        xaxis=dict(tickfont=dict(color="#FFFFFF")),
        yaxis=dict(tickfont=dict(color="#FFFFFF"), range=[0, 5]),
        legend=dict(font=dict(color="#FFFFFF")),
        width = 800,
        height = 800
    )

    return fig

def generate_bps_figure(bps_df, bps_column_mapping, patient_id):
    """
    Generates a Plotly figure comparing individual BPS scores with the average scores.

    Parameters:
    - bps_df: DataFrame containing the BPS data.
    - bps_column_mapping: Mapping of BPS columns to actual column names.
    - patient_id: The patient ID for filtering the data.

    Returns:
    - A Plotly figure object.
    """
    # Filter for the given patient_id
    filtered_df = bps_df[bps_df['group_identifier'] == patient_id]

    # Select relevant BPS columns (exclude 'Total')
    bps_cols = [col for col in bps_column_mapping.values() if col != "Total"]
    
    # Compute aggregates for the BPS columns
    bps_aggregates = bps_df[bps_cols].agg(['mean', 'median']).transpose()
    individual_scores = filtered_df[bps_cols].iloc[0]
    
    # Compute patient's total BPS score
    patient_ban = filtered_df[bps_cols].sum(axis=1).iloc[0]
    total_bps_avg = bps_df[bps_cols].sum(axis=1).mean()

    # Prepare data for bar plot
    plot_df = pd.DataFrame({
        'Category': bps_cols,
        'Average Score': bps_aggregates['mean'],
        'Individual Score': individual_scores
    }).melt(id_vars=['Category'], value_vars=['Average Score', 'Individual Score'], var_name='Type', value_name='Score')

    # bar plot
    fig = px.bar(plot_df, x='Category', y='Score', color='Type', barmode='group',
                 title=f"Individual Score vs Average Scores for Patient: {patient_id}",
                 color_discrete_map={"Average Score": "#00BCD4", "Individual Score": "#FF5722"})
    
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="'Inter', sans-serif", size=18, color="#FFFFFF"),
        title_font=dict(family="'Inter', sans-serif", size=26, color="#FFFFFF"),
        xaxis=dict(tickfont=dict(color="#FFFFFF")),
        yaxis=dict(tickfont=dict(color="#FFFFFF"), range=[0, 5]),
        legend=dict(font=dict(size=18, color="#FFFFFF"))
    )
    fig.update_traces(hovertemplate="%{x}:<br>Score: %{y}<br><br>Rating/Severity Scale:<br>0 - Not at all<br>1 - Slightly<br>2 - Moderately<br>3 - Considerably<br>4 - Extremely<br><extra></extra>")

    return fig
