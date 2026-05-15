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
df['Size'] = pd.to_numeric(df['Size'], errors='coerce')
df['Installs'] = df['Installs'].str.replace('+', '', regex=False).str.replace(',', '', regex=False)
df['Installs'] = pd.to_numeric(df['Installs'], errors='coerce')
df['Price'] = df['Price'].str.replace('$', '', regex=False)
df['Price'] = df['Price'].replace('Everyone', '0')
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

app.layout = html.Div([
    html.Div([
        html.H1("📱 Google Play Store Analytics Dashboard",
                style={'textAlign': 'center', 'color': 'white', 'marginBottom': 10}),
        html.P("Interactive analysis of app store performance metrics", 
               style={'textAlign': 'center', 'color': 'white', 'marginBottom': 30})
    ], style={'backgroundColor': '#2C3E50', 'padding': '20px', 'borderRadius': '10px'}),

    html.Div([
        # Controls
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

        # Main chart
        html.Div([
            dcc.Graph(id='main-chart', style={'height': '500px'})
        ], style={'backgroundColor': 'white', 'padding': '15px', 'borderRadius': '10px', 'boxShadow': '0 4px 6px rgba(0,0,0,0.1)', 'marginBottom': '20px'}),

        # Secondary chart for correlations
        html.Div([
            dcc.Graph(id='secondary-chart', style={'height': '400px'})
        ], style={'backgroundColor': 'white', 'padding': '15px', 'borderRadius': '10px', 'boxShadow': '0 4px 6px rgba(0,0,0,0.1)', 'marginBottom': '20px'}),

        # Additional metrics
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

    if comparison_type == 'categories':
        # Top categories by app count
        category_counts = df_clean['Category'].value_counts().head(item_count)

        main_fig = px.bar(
            x=category_counts.values,
            y=category_counts.index,
            orientation='h',
            title=f'Top {item_count} Categories by Number of Apps',
            color=category_counts.values,
            color_continuous_scale='Viridis'
        )
        main_fig.update_layout(
            xaxis_title="Number of Apps",
            yaxis_title="Category",
            showlegend=False
        )

        # Secondary: Category by average rating
        avg_ratings = df_clean.groupby('Category')['Rating'].mean().loc[category_counts.index]
        secondary_fig = px.bar(
            x=avg_ratings.values,
            y=avg_ratings.index,
            orientation='h',
            title=f'Average Ratings for Top {item_count} Categories',
            color=avg_ratings.values,
            color_continuous_scale='Plasma'
        )
        secondary_fig.update_layout(showlegend=False)

    elif comparison_type == 'reviews':
        # Top apps by reviews
        top_apps_df = df_clean.nlargest(item_count, 'Reviews')

        main_fig = px.bar(
            top_apps_df,
            x='Reviews',
            y='App',
            orientation='h',
            title=f'Top {item_count} Apps by Number of Reviews',
            color='Rating',
            color_continuous_scale='Plasma'
        )
        main_fig.update_layout(
            xaxis_title="Number of Reviews",
            yaxis_title="App Name"
        )

        # Secondary: Reviews vs Rating scatter
        secondary_fig = px.scatter(
            top_apps_df,
            x='Reviews',
            y='Rating',
            size='Installs',
            color='Category',
            title='Reviews vs Rating (Size = Installs)',
            hover_data=['App'],
            color_discrete_sequence=bag_colors
        )

    elif comparison_type == 'ratings':
        # Rating distribution by top categories
        top_cats = df_clean['Category'].value_counts().head(item_count).index
        filtered_df = df_clean[df_clean['Category'].isin(top_cats)]

        main_fig = px.box(
            filtered_df,
            x='Category',
            y='Rating',
            title=f'Rating Distribution for Top {item_count} Categories',
            color='Category',
            color_discrete_sequence=bag_colors[:item_count]
        )
        main_fig.update_layout(xaxis_tickangle=45)

        # Secondary: Rating distribution histogram
        secondary_fig = px.histogram(
            df_clean,
            x='Rating',
            title='Overall Rating Distribution',
            color_discrete_sequence=['#FF6B6B']
        )

    elif comparison_type == 'pricing':
        # Free vs Paid apps comparison
        pricing_data = df_clean['Type'].value_counts()

        main_fig = px.pie(
            names=pricing_data.index,
            values=pricing_data.values,
            title='Free vs Paid Apps Distribution',
            color=pricing_data.index,
            color_discrete_sequence=['#4ECDC4', '#FF6B6B']
        )

        # Secondary: Average rating by type
        avg_rating_by_type = df_clean.groupby('Type')['Rating'].mean()
        secondary_fig = px.bar(
            x=avg_rating_by_type.index,
            y=avg_rating_by_type.values,
            title='Average Rating by App Type',
            color=avg_rating_by_type.index,
            color_discrete_sequence=['#4ECDC4', '#FF6B6B']
        )

    elif comparison_type == 'correlation':
        # Rating vs Reviews correlation
        sample_df = df_clean.nlargest(item_count * 10, 'Reviews')  # Larger sample for better visualization

        main_fig = px.scatter(
            sample_df,
            x='Rating',
            y='Reviews',
            size='Installs',
            color='Category',
            title='Rating vs Reviews Correlation (Size = Installs)',
            hover_data=['App'],
            color_discrete_sequence=bag_colors,
            log_y=True
        )

        # Secondary: Correlation heatmap for numerical columns
        corr_df = df_clean[['Rating', 'Reviews', 'Installs', 'Price']].corr()
        secondary_fig = px.imshow(
            corr_df,
            title='Feature Correlation Heatmap',
            color_continuous_scale='RdBu_r',
            aspect='auto'
        )

    elif comparison_type == 'installs':
        # Top apps by installs
        top_installs_df = df_clean.nlargest(item_count, 'Installs')

        main_fig = px.bar(
            top_installs_df,
            x='Installs',
            y='App',
            orientation='h',
            title=f'Top {item_count} Apps by Number of Installs',
            color='Rating',
            color_continuous_scale='Viridis'
        )
        main_fig.update_layout(xaxis_type='log')

        # Secondary: Installs by category
        installs_by_category = df_clean.groupby('Category')['Installs'].sum().nlargest(item_count)
        secondary_fig = px.bar(
            x=installs_by_category.values,
            y=installs_by_category.index,
            orientation='h',
            title=f'Total Installs by Top {item_count} Categories',
            color=installs_by_category.values,
            color_continuous_scale='Plasma'
        )
        secondary_fig.update_layout(xaxis_type='log')

    elif comparison_type == 'content_rating':
        # Content rating distribution
        content_rating_data = df_clean['Content Rating'].value_counts()

        main_fig = px.pie(
            names=content_rating_data.index,
            values=content_rating_data.values,
            title='Content Rating Distribution',
            color=content_rating_data.index,
            color_discrete_sequence=bag_colors[:len(content_rating_data)]
        )

        # Secondary: Average rating by content rating
        avg_rating_by_content = df_clean.groupby('Content Rating')['Rating'].mean()
        secondary_fig = px.bar(
            x=avg_rating_by_content.index,
            y=avg_rating_by_content.values,
            title='Average Rating by Content Rating',
            color=avg_rating_by_content.index,
            color_discrete_sequence=bag_colors[:len(avg_rating_by_content)]
        )

    elif comparison_type == 'updates':
        # Apps by update year
        yearly_updates = df_clean['Year'].value_counts().sort_index().tail(item_count)

        main_fig = px.line(
            x=yearly_updates.index,
            y=yearly_updates.values,
            title=f'App Updates by Year (Last {item_count} Years)',
            markers=True
        )
        main_fig.update_traces(line_color='#FF6B6B', marker_color='#45B7D1')
        main_fig.update_layout(xaxis_title="Year", yaxis_title="Number of Updates")

        # Secondary: Average rating by year
        yearly_ratings = df_clean.groupby('Year')['Rating'].mean().tail(item_count)
        secondary_fig = px.line(
            x=yearly_ratings.index,
            y=yearly_ratings.values,
            title=f'Average Rating by Year (Last {item_count} Years)',
            markers=True
        )
        secondary_fig.update_traces(line_color='#4ECDC4', marker_color='#96CEB4')

    elif comparison_type == 'price_dist':
        # Price distribution
        paid_apps = df_clean[df_clean['Price'] > 0]

        main_fig = px.histogram(
            paid_apps,
            x='Price',
            title='Price Distribution for Paid Apps',
            nbins=20,
            color_discrete_sequence=['#FF6B6B']
        )
        main_fig.update_layout(xaxis_title="Price ($)", yaxis_title="Number of Apps")

        # Secondary: Most expensive apps
        expensive_apps = paid_apps.nlargest(item_count, 'Price')
        secondary_fig = px.bar(
            expensive_apps,
            x='Price',
            y='App',
            orientation='h',
            title=f'Top {item_count} Most Expensive Apps',
            color='Rating',
            color_continuous_scale='Viridis'
        )

    elif comparison_type == 'size_analysis':
        # App size analysis
        size_data = df_clean.dropna(subset=['Size']).nlargest(item_count, 'Size')

        main_fig = px.bar(
            size_data,
            x='Size',
            y='App',
            orientation='h',
            title=f'Top {item_count} Largest Apps by Size',
            color='Rating',
            color_continuous_scale='Plasma'
        )

        # Secondary: Size vs Rating
        secondary_fig = px.scatter(
            df_clean.dropna(subset=['Size']).nlargest(100, 'Reviews'),
            x='Size',
            y='Rating',
            size='Installs',
            color='Category',
            title='App Size vs Rating (Top 100 by Reviews)',
            hover_data=['App'],
            color_discrete_sequence=bag_colors
        )

    # Quick stats
    stats.extend([
        html.Div([
            html.H5("📱 Total Apps", style={'color': '#2C3E50', 'margin': '0'}),
            html.H3(f"{len(df_clean):,}", style={'color': '#E74C3C', 'margin': '0'})
        ], style={'textAlign': 'center', 'padding': '15px', 'backgroundColor': 'white', 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),

        html.Div([
            html.H5("⭐ Avg Rating", style={'color': '#2C3E50', 'margin': '0'}),
            html.H3(f"{df_clean['Rating'].mean():.2f}", style={'color': '#E74C3C', 'margin': '0'})
        ], style={'textAlign': 'center', 'padding': '15px', 'backgroundColor': 'white', 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),

        html.Div([
            html.H5("⬇ Avg Installs", style={'color': '#2C3E50', 'margin': '0'}),
            html.H3(f"{df_clean['Installs'].mean():,.0f}", style={'color': '#E74C3C', 'margin': '0'})
        ], style={'textAlign': 'center', 'padding': '15px', 'backgroundColor': 'white', 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),

        html.Div([
            html.H5("💰 Free Apps %", style={'color': '#2C3E50', 'margin': '0'}),
            html.H3(f"{(df_clean['Type'] == 'Free').mean()*100:.1f}%", style={'color': '#E74C3C', 'margin': '0'})
        ], style={'textAlign': 'center', 'padding': '15px', 'backgroundColor': 'white', 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'})
    ])

    return main_fig, secondary_fig, stats

if __name__ == '__main__':
    app.run(debug=True, port=8050)