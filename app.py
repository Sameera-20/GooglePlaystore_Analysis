import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import numpy as np


# CLEAN SIZE FUNCTION
-
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



# LOAD DATA

df = pd.read_csv('googleplaystore.csv')

# DATA CLEANING

df['Rating'] = pd.to_numeric(df['Rating'], errors='coerce')
df['Reviews'] = pd.to_numeric(df['Reviews'], errors='coerce')

# FIX SIZE
df['Size'] = df['Size'].apply(clean_size)

# FIX INSTALLS
df['Installs'] = df['Installs'].str.replace('+', '', regex=False)
df['Installs'] = df['Installs'].str.replace(',', '', regex=False)
df['Installs'] = pd.to_numeric(df['Installs'], errors='coerce')

# FIX PRICE
df['Price'] = df['Price'].str.replace('$', '', regex=False)
df['Price'] = pd.to_numeric(df['Price'], errors='coerce')

# DATE HANDLING
df['Last Updated'] = pd.to_datetime(df['Last Updated'], errors='coerce')
df['Year'] = df['Last Updated'].dt.year

# REMOVE DUPLICATES
df = df.drop_duplicates(subset=['App'])

# CLEAN DATASET
df_clean = df.dropna(subset=['Rating', 'Reviews', 'Installs']).copy()


# COLORS

bag_colors = [
    '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4',
    '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F',
    '#BB8FCE', '#85C1E9'
]


# DASH APP

app = dash.Dash(__name__)
server = app.server

# LAYOUT

app.layout = html.Div([

    html.Div([
        html.H1(
            "📱 Google Play Store Analytics Dashboard",
            style={
                'textAlign': 'center',
                'color': 'white'
            }
        ),

        html.P(
            "Interactive Dashboard using Dash + Plotly",
            style={
                'textAlign': 'center',
                'color': 'white'
            }
        )
    ], style={
        'backgroundColor': '#2C3E50',
        'padding': '20px',
        'borderRadius': '10px'
    }),

    html.Br(),

    html.Div([

        html.Label(
            "Select Analysis Type",
            style={
                'fontWeight': 'bold',
                'fontSize': '18px'
            }
        ),

        dcc.Dropdown(
            id='comparison-type',
            options=[
                {'label': 'Top Categories', 'value': 'categories'},
                {'label': 'Top Apps by Reviews', 'value': 'reviews'},
                {'label': 'Rating Distribution', 'value': 'ratings'},
                {'label': 'Free vs Paid', 'value': 'pricing'},
                {'label': 'Top Installs', 'value': 'installs'},
                {'label': 'App Updates by Year', 'value': 'updates'}
            ],
            value='categories'
        ),

        html.Br(),

        html.Label(
            "Number of Items",
            style={
                'fontWeight': 'bold',
                'fontSize': '18px'
            }
        ),

        dcc.Slider(
            id='item-count',
            min=5,
            max=20,
            step=1,
            value=10,
            marks={i: str(i) for i in range(5, 21, 5)}
        )

    ], style={
        'backgroundColor': 'white',
        'padding': '20px',
        'borderRadius': '10px'
    }),

    html.Br(),

    html.Div([
        dcc.Graph(id='main-chart')
    ], style={
        'backgroundColor': 'white',
        'padding': '10px',
        'borderRadius': '10px'
    }),

    html.Br(),

    html.Div([
        dcc.Graph(id='secondary-chart')
    ], style={
        'backgroundColor': 'white',
        'padding': '10px',
        'borderRadius': '10px'
    }),

    html.Br(),

    html.Div(
        id='quick-stats',
        style={
            'display': 'grid',
            'gridTemplateColumns': 'repeat(4, 1fr)',
            'gap': '10px'
        }
    )

], style={
    'backgroundColor': '#F4F6F7',
    'padding': '20px'
})


# CALLBACK

@app.callback(
    [
        Output('main-chart', 'figure'),
        Output('secondary-chart', 'figure'),
        Output('quick-stats', 'children')
    ],
    [
        Input('comparison-type', 'value'),
        Input('item-count', 'value')
    ]
)
def update_dashboard(comparison_type, item_count):

    main_fig = go.Figure()
    secondary_fig = go.Figure()

   
    # CATEGORY ANALYSIS
    
    if comparison_type == 'categories':

        category_counts = (
            df_clean['Category']
            .value_counts()
            .head(item_count)
        )

        main_fig = px.bar(
            x=category_counts.values,
            y=category_counts.index,
            orientation='h',
            title='Top Categories by App Count',
            color=category_counts.values,
            color_continuous_scale='Viridis'
        )

        avg_ratings = (
            df_clean.groupby('Category')['Rating']
            .mean()
            .loc[category_counts.index]
        )

        secondary_fig = px.bar(
            x=avg_ratings.values,
            y=avg_ratings.index,
            orientation='h',
            title='Average Ratings by Category',
            color=avg_ratings.values,
            color_continuous_scale='Plasma'
        )

    
    # REVIEWS ANALYSIS
 
    elif comparison_type == 'reviews':

        top_apps = df_clean.nlargest(item_count, 'Reviews')

        main_fig = px.bar(
            top_apps,
            x='Reviews',
            y='App',
            orientation='h',
            title='Top Apps by Reviews',
            color='Rating',
            color_continuous_scale='Plasma'
        )

        secondary_fig = px.scatter(
            top_apps,
            x='Reviews',
            y='Rating',
            size='Installs',
            color='Category',
            hover_data=['App'],
            title='Reviews vs Rating'
        )

   
    # RATING ANALYSIS
   
    elif comparison_type == 'ratings':

        top_cats = (
            df_clean['Category']
            .value_counts()
            .head(item_count)
            .index
        )

        filtered_df = df_clean[
            df_clean['Category'].isin(top_cats)
        ]

        main_fig = px.box(
            filtered_df,
            x='Category',
            y='Rating',
            color='Category',
            title='Rating Distribution by Category'
        )

        secondary_fig = px.histogram(
            df_clean,
            x='Rating',
            nbins=20,
            title='Overall Rating Distribution'
        )

    # FREE VS PAID
   
    elif comparison_type == 'pricing':

        pricing_data = df_clean['Type'].value_counts()

        main_fig = px.pie(
            names=pricing_data.index,
            values=pricing_data.values,
            title='Free vs Paid Apps'
        )

        avg_rating = (
            df_clean.groupby('Type')['Rating']
            .mean()
        )

        secondary_fig = px.bar(
            x=avg_rating.index,
            y=avg_rating.values,
            title='Average Rating by Type'
        )

    
    # INSTALLS
 
    elif comparison_type == 'installs':

        top_installs = df_clean.nlargest(item_count, 'Installs')

        main_fig = px.bar(
            top_installs,
            x='Installs',
            y='App',
            orientation='h',
            title='Top Apps by Installs',
            color='Rating',
            color_continuous_scale='Viridis'
        )

        installs_by_cat = (
            df_clean.groupby('Category')['Installs']
            .sum()
            .nlargest(item_count)
        )

        secondary_fig = px.bar(
            x=installs_by_cat.values,
            y=installs_by_cat.index,
            orientation='h',
            title='Total Installs by Category'
        )

   
    # UPDATES
    
    elif comparison_type == 'updates':

        yearly_updates = (
            df_clean['Year']
            .value_counts()
            .sort_index()
        )

        main_fig = px.line(
            x=yearly_updates.index,
            y=yearly_updates.values,
            markers=True,
            title='Apps Updated by Year'
        )

        yearly_rating = (
            df_clean.groupby('Year')['Rating']
            .mean()
        )

        secondary_fig = px.line(
            x=yearly_rating.index,
            y=yearly_rating.values,
            markers=True,
            title='Average Rating by Year'
        )

    
    # QUICK STATS

    stats = [

        html.Div([
            html.H4("📱 Total Apps"),
            html.H2(f"{len(df_clean):,}")
        ], style={
            'backgroundColor': 'white',
            'padding': '20px',
            'borderRadius': '10px',
            'textAlign': 'center'
        }),

        html.Div([
            html.H4("⭐ Avg Rating"),
            html.H2(f"{df_clean['Rating'].mean():.2f}")
        ], style={
            'backgroundColor': 'white',
            'padding': '20px',
            'borderRadius': '10px',
            'textAlign': 'center'
        }),

        html.Div([
            html.H4("⬇ Avg Installs"),
            html.H2(f"{df_clean['Installs'].mean():,.0f}")
        ], style={
            'backgroundColor': 'white',
            'padding': '20px',
            'borderRadius': '10px',
            'textAlign': 'center'
        }),

        html.Div([
            html.H4("💰 Free Apps %"),
            html.H2(
                f"{(df_clean['Type'] == 'Free').mean() * 100:.1f}%"
            )
        ], style={
            'backgroundColor': 'white',
            'padding': '20px',
            'borderRadius': '10px',
            'textAlign': 'center'
        })
    ]

    return main_fig, secondary_fig, stats



# RUN APP

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8050)
