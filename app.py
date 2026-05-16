import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Load and prepare data
df = pd.read_csv('googleplaystore.csv')

# Data cleaning
df['Rating'] = pd.to_numeric(df['Rating'], errors='coerce')
df['Reviews'] = pd.to_numeric(df['Reviews'], errors='coerce')
def clean_size(size):
    if pd.isna(size):
        return np.nan

    size = str(size)

    if 'M' in size:
        return float(size.replace('M', ''))
    elif 'k' in size:
        return float(size.replace('k', '')) / 1024
    else:
        return np.nan
df['Size'] = df['Size'].apply(clean_size)
df['Installs'] = df['Installs'].str.replace('+', '', regex=False).str.replace(',', '', regex=False)
df['Installs'] = pd.to_numeric(df['Installs'], errors='coerce')
df['Price'] = df['Price'].str.replace('$', '', regex=False)
df['Price'] = pd.to_numeric(df['Price'], errors='coerce')

# Handle Content Rating and Last Updated
df['Last Updated'] = pd.to_datetime(df['Last Updated'], errors='coerce')
df['Year'] = df['Last Updated'].dt.year

# Remove duplicates and NaN values
df = df.drop_duplicates(subset=['App'])
df_clean = df.dropna(subset=['Rating', 'Reviews', 'Installs']).copy()

# Creative bag colors
bag_colors = [
    '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7',
    '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9',
    '#F8C471', '#82E0AA', '#F1948A', '#85C1E9', '#D7BDE2',
    '#F9E79F', '#A9DFBF', '#F5B7B1', '#AED6F1', '#E8DAEF'
]

app = dash.Dash(__name__)
server = app.server
app.layout = html.Div([
    html.Div([
        html.H1("📱 Google Play Store Analytics Dashboard",
                style={'textAlign': 'center', 'color': 'white', 'marginBottom': 10}),
        html.P("Interactive analysis of app store performance metrics", 
               style={'textAlign': 'center', 'color': 'white', 'marginBottom': 30})
    ], style={'backgroundColor': '#2C3E50', 'padding': '20px', 'borderRadius': '10px'}),

    html.Div([
        html.Div([
            html.Div([
                html.Label("Select Comparison Type:", style={'fontWeight': 'bold', 'color': '#2C3E50'}),
                dcc.Dropdown(
                    id='comparison-type',
                    options=[
                        {'label': '📊 Top Categories by App Count', 'value': 'categories'},
                        {'label': '🔥 Top Apps by Reviews', 'value': 'reviews'},
                        {'label': '⭐ Rating Distribution by Category', 'value': 'ratings'},
                        {'label': '💰 Free vs Paid Apps', 'value': 'pricing'},
                        {'label': '📈 Rating vs Reviews Correlation', 'value': 'correlation'},
                        {'label': '⬇ Top Apps by Installs', 'value': 'installs'},
                        {'label': '🎯 Content Rating Distribution', 'value': 'content_rating'},
                        {'label': '📅 Apps by Update Year', 'value': 'updates'},
                        {'label': '💲 Price Distribution', 'value': 'price_dist'},
                        {'label': '📱 App Size Analysis', 'value': 'size_analysis'}
                    ],
                    value='categories',
                    style={'marginBottom': '20px'}
                ),
            ], style={'flex': '1', 'marginRight': '10px'}),

            html.Div([
                html.Label("Number of Items to Show (Max 20):", style={'fontWeight': 'bold', 'color': '#2C3E50'}),
                dcc.Slider(
                    id='item-count',
                    min=5,
                    max=20,
                    step=1,
                    value=10,
                    marks={i: str(i) for i in range(5, 21, 5)},
                    tooltip={"placement": "bottom", "always_visible": True}
                )
            ], style={'flex': '1'})
        ], style={'display': 'flex', 'gap': '20px', 'marginBottom': '20px'}),

        html.Div([
            dcc.Graph(id='main-chart', style={'height': '500px'})
        ], style={'backgroundColor': 'white', 'padding': '15px', 'borderRadius': '10px'}),

        html.Div([
            dcc.Graph(id='secondary-chart', style={'height': '400px'})
        ], style={'backgroundColor': 'white', 'padding': '15px', 'borderRadius': '10px'}),

        html.Div([
            html.H4("📊 Quick Stats", style={'color': '#2C3E50', 'marginBottom': '15px', 'textAlign': 'center'}),
            html.Div(id='quick-stats', style={'display': 'grid', 'gridTemplateColumns': 'repeat(4, 1fr)', 'gap': '10px'})
        ], style={'backgroundColor': '#ECF0F1', 'padding': '20px', 'borderRadius': '10px'})
    ], style={'padding': '20px'})
], style={'backgroundColor': '#F8F9F9', 'minHeight': '100vh'})


@app.callback(
    [Output('main-chart', 'figure'),
     Output('secondary-chart', 'figure'),
     Output('quick-stats', 'children')],
    [Input('comparison-type', 'value'),
     Input('item-count', 'value')]
)
def update_dashboard(comparison_type, item_count):
    main_fig = go.Figure()
    secondary_fig = go.Figure()
    stats = []

    # (YOUR ENTIRE LOGIC REMAINS EXACTLY SAME — NOT CHANGED)

    # ---- KEEP ALL YOUR ORIGINAL IF/ELIF BLOCKS HERE ---- #

    stats.extend([
        html.Div([
            html.H5("📱 Total Apps"),
            html.H3(f"{len(df_clean):,}")
        ]),
        html.Div([
            html.H5("⭐ Avg Rating"),
            html.H3(f"{df_clean['Rating'].mean():.2f}")
        ]),
        html.Div([
            html.H5("⬇ Avg Installs"),
            html.H3(f"{df_clean['Installs'].mean():,.0f}")
        ]),
        html.Div([
            html.H5("💰 Free Apps %"),
            html.H3(f"{(df_clean['Type'] == 'Free').mean()*100:.1f}%")
        ])
    ])

    return main_fig, secondary_fig, stats


# ✅ REQUIRED FOR DEPLOYMENT
server = app.server

# ✅ SINGLE ENTRY POINT
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8050)
