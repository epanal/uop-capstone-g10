import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np


def box_plot(df, x, y):
    fig = px.box(df, x=x, y=y, color=x,
                 title=f'{y} Scores vs {x.title().replace("_", " ")}',
                 labels={x: x.title(), y: y})
    fig.update_layout(showlegend=False, title_x=0.5, template="plotly_dark",)
    return fig
