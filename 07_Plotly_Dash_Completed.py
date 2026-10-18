"""IBM SpaceX Capstone — Lab 07: Interactive Plotly Dash dashboard.

Place spacex_launch_dash.csv in the same folder and run:
    python 07_Plotly_Dash_Completed.py
Then open http://127.0.0.1:8050/ (or Coursera's Launch Application on port 8050).
"""
from pathlib import Path

import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px

DATA_PATH = Path(__file__).resolve().parent / 'spacex_launch_dash.csv'
spacex_df = pd.read_csv(DATA_PATH)
required = {'Launch Site', 'class', 'Payload Mass (kg)', 'Booster Version Category'}
missing = required - set(spacex_df.columns)
if missing:
    raise ValueError(f'Missing required CSV columns: {sorted(missing)}')

spacex_df['class'] = pd.to_numeric(spacex_df['class'], errors='raise').astype(int)
spacex_df['Payload Mass (kg)'] = pd.to_numeric(spacex_df['Payload Mass (kg)'], errors='coerce')
spacex_df = spacex_df.dropna(subset=['Payload Mass (kg)'])
site_options = [{'label': 'All Sites', 'value': 'ALL'}] + [
    {'label': site, 'value': site} for site in sorted(spacex_df['Launch Site'].unique())
]

app = Dash(__name__)
app.title = 'SpaceX Launch Records Dashboard'
app.layout = html.Div([
    html.H1('SpaceX Launch Records Dashboard', style={'textAlign': 'center', 'color': '#503D36'}),
    html.Label('Select a Launch Site'),
    # TASK 1: Site dropdown
    dcc.Dropdown(id='site-dropdown', options=site_options, value='ALL',
                 placeholder='Select a Launch Site here', searchable=True, clearable=False),
    html.Br(),
    # TASK 2: Site-dependent success pie chart
    dcc.Graph(id='success-pie-chart'),
    html.Br(),
    html.P('Payload range (kg):'),
    # TASK 3: Payload range slider
    dcc.RangeSlider(id='payload-slider', min=0, max=10000, step=1000,
                    marks={i: str(i) for i in range(0, 10001, 2000)},
                    value=[0, 10000], allowCross=False),
    html.Br(),
    # TASK 4: Payload/outcome scatter plot
    dcc.Graph(id='success-payload-scatter-chart'),
], style={'maxWidth': '1200px', 'margin': '0 auto', 'padding': '20px',
          'fontFamily': 'Arial, sans-serif'})


@app.callback(Output('success-pie-chart', 'figure'), Input('site-dropdown', 'value'))
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        successes = (spacex_df[spacex_df['class'] == 1]
                     .groupby('Launch Site').size().reset_index(name='Successful Launches'))
        fig = px.pie(successes, values='Successful Launches', names='Launch Site',
                     title='Successful Launches by Site (All Sites)', hole=0.0)
    else:
        filtered = spacex_df[spacex_df['Launch Site'] == entered_site]
        outcomes = (filtered['class'].value_counts().reindex([0, 1], fill_value=0)
                    .rename_axis('class').reset_index(name='Launch Count'))
        outcomes['Outcome'] = outcomes['class'].map({0: 'Failed', 1: 'Successful'})
        fig = px.pie(outcomes, values='Launch Count', names='Outcome',
                     title=f'Launch Outcomes at {entered_site}',
                     color='Outcome', color_discrete_map={'Failed': '#e45756', 'Successful': '#54a24b'})
    fig.update_layout(margin=dict(l=20, r=20, t=65, b=20))
    return fig


@app.callback(Output('success-payload-scatter-chart', 'figure'),
              Input('site-dropdown', 'value'), Input('payload-slider', 'value'))
def get_scatter_chart(entered_site, payload_range):
    low, high = payload_range
    filtered = spacex_df[spacex_df['Payload Mass (kg)'].between(low, high)].copy()
    if entered_site != 'ALL':
        filtered = filtered[filtered['Launch Site'] == entered_site]
    fig = px.scatter(filtered, x='Payload Mass (kg)', y='class',
                     color='Booster Version Category', hover_data=['Launch Site', 'Flight Number'],
                     title=f'Payload Mass vs. Landing Outcome — {"All Sites" if entered_site == "ALL" else entered_site}',
                     labels={'class': 'Landing Outcome (0 = Failed, 1 = Successful)'})
    fig.update_yaxes(tickvals=[0, 1], range=[-0.2, 1.2])
    fig.update_layout(margin=dict(l=20, r=20, t=65, b=20))
    return fig


if __name__ == '__main__':
    print(f'Loaded {len(spacex_df)} launch records from {DATA_PATH.name}')
    print('Dashboard: http://127.0.0.1:8050/')
    app.run(host='0.0.0.0', port=8050, debug=False)
