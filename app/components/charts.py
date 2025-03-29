import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd
import numpy as np

def get_consumption_chart():
    # Generate sample data: hourly data for January 2023
    date_rng = pd.date_range(start='2023-01-01', end='2023-01-31 23:00', freq='H')
    consumption = np.random.randint(100, 200, size=len(date_rng))  # sample consumption values

    # Create a DataFrame
    df = pd.DataFrame({'Date': date_rng, 'Consumption': consumption})

    # Create an interactive line chart using Plotly Express
    fig = px.line(
        df, 
        x='Date', 
        y='Consumption', 
        title='Electricity Consumption in France',
        labels={'Consumption': 'Consumption (MW)'}
    )
    fig.update_layout(hovermode='x unified')
    
    # Return the graph component
    return dcc.Graph(id='consumption-chart', figure=fig)
