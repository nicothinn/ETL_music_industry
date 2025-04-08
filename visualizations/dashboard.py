from collections import Counter
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
from sqlalchemy import create_engine

engine = create_engine('postgresql://postgres:postgres@localhost:5432/postgres')
df = pd.read_sql("SELECT * FROM music_dataset", engine)

if 'explicit' in df.columns:
    explicit_counts = df['explicit'].value_counts()
    pie_chart = px.pie(
        names=explicit_counts.index.map(lambda x: 'Explicit' if x else 'Non-Explicit'),
        values=explicit_counts.values,
        title="🔞 Explicit vs Non-Explicit Songs",
        color_discrete_sequence=px.colors.qualitative.Bold
    )
else:
    pie_chart = go.Figure()

popularity_hist = px.histogram(
    df,
    x="popularity",
    nbins=20,
    title="🎧 Popularity Distribution",
    labels={"popularity": "Popularity", "count": "Number of Songs"},
    template="plotly_white",
    color_discrete_sequence=px.colors.sequential.Rainbow
)

top_billboard = (
    df[df['total_weeks_on_chart'].notna() & (df['total_weeks_on_chart'] < 500)]
    .sort_values('total_weeks_on_chart', ascending=False)
    .head(20)
)

top_billboard_sorted = top_billboard.sort_values("total_weeks_on_chart", ascending=True)

top_billboard_chart = px.bar(
    top_billboard_sorted,
    x="total_weeks_on_chart",
    y="song_name",
    orientation='h',
    title="📈 Songs with Most Weeks on Billboard",
    labels={"total_weeks_on_chart": "Weeks on Billboard", "song_name": "Song"},
    category_orders={"song_name": top_billboard_sorted['song_name'].tolist()},
    template="plotly_white",
    color_discrete_sequence=px.colors.qualitative.Set3
)

top_number_one = (
    df[(df['billboard_peak'] == 1) & df['total_weeks_on_chart'].notna() & (df['total_weeks_on_chart'] < 500)]
    .sort_values('total_weeks_on_chart', ascending=False)
    .head(10)
)

top_number_one_sorted = top_number_one.sort_values("total_weeks_on_chart", ascending=True)

top_number_one_chart = px.bar(
    top_number_one_sorted,
    x="total_weeks_on_chart",
    y="song_name",
    orientation='h',
    title="🥇 Top 10 Songs that Stayed #1 on Billboard the Longest",
    labels={"total_weeks_on_chart": "Weeks at #1", "song_name": "Song"},
    category_orders={"song_name": top_number_one_sorted['song_name'].tolist()},
    template="plotly_white",
    color_discrete_sequence=px.colors.qualitative.Prism
)

top_grammy_artists = (
    df[df['category'].notna()]
    .groupby('artist')
    .size()
    .reset_index(name='grammy_wins')
    .sort_values('grammy_wins', ascending=False)
    .head(10)
)

top_grammy_sorted = top_grammy_artists.sort_values("grammy_wins", ascending=True)

top_grammy_chart = px.bar(
    top_grammy_sorted,
    x='grammy_wins',
    y='artist',
    orientation='h',
    title="🏆 Top Grammy-Winning Artists",
    labels={"artist": "Artist", "grammy_wins": "Number of Grammy Wins"},
    category_orders={"artist": top_grammy_sorted['artist'].tolist()},
    template="plotly_white",
    color_discrete_sequence=px.colors.qualitative.Set1
)

treemap = px.treemap(
    top_billboard,
    path=[px.Constant("Top Songs"), 'artist', 'song_name'],
    values='total_weeks_on_chart',
    color='total_weeks_on_chart',
    color_continuous_scale='Tealgrn',
    color_continuous_midpoint=np.average(top_billboard['total_weeks_on_chart']),
    title="🌳 Treemap of Top 20 Songs by Billboard Weeks"
)
treemap.update_layout(margin=dict(t=50, l=25, r=25, b=25))

danceability_by_genre_mean = (
    df[df['danceability'].notna() & df['track_genre'].notna()]
    .groupby('track_genre')['danceability']
    .mean()
    .sort_values(ascending=False)
    .reset_index()
)

danceability_mean_chart = px.bar(
    danceability_by_genre_mean,
    x='danceability',
    y='track_genre',
    orientation='h',
    title='🎼 Average Danceability by Genre',
    labels={'track_genre': 'Genre', 'danceability': 'Average Danceability'},
    template='plotly_white',
    color_discrete_sequence=px.colors.qualitative.T10
)

danceability_mean_chart.update_layout(yaxis={'categoryorder': 'total ascending'})

correlation_features = [
    'popularity', 'tempo', 'valence', 'energy', 'danceability', 'acousticness', 'duration_minutes'
]

correlation_df = df[correlation_features].dropna()
correlation_matrix = correlation_df.corr()

correlation_heatmap = px.imshow(
    correlation_matrix,
    text_auto=True,
    color_continuous_scale='RdBu_r',
    title='📊 Feature Correlation Heatmap',
    labels=dict(color="Correlation Coefficient")
)

app = Dash(__name__)
app.title = "🎵 Music Insights"

app.layout = html.Div([
    html.H1("🎶 Music Industry Dashboard", style={"textAlign": "center"}),

    html.Div([
        html.Div([dcc.Graph(figure=pie_chart)], style={"width": "48%", "display": "inline-block", "padding": "10px"}),
        html.Div([dcc.Graph(figure=popularity_hist)], style={"width": "48%", "display": "inline-block", "padding": "10px"})
    ]),

    html.Div([
        html.Div([dcc.Graph(figure=top_number_one_chart)], style={"width": "48%", "display": "inline-block", "padding": "10px"}),
        html.Div([dcc.Graph(figure=top_grammy_chart)], style={"width": "48%", "display": "inline-block", "padding": "10px"})
    ]),

    html.Div([
        html.Div([dcc.Graph(figure=treemap)], style={"width": "48%", "display": "inline-block", "padding": "10px"}),
        html.Div([dcc.Graph(figure=danceability_mean_chart)], style={"width": "48%", "display": "inline-block", "padding": "10px"})
    ]),

    html.Div([
        dcc.Graph(figure=correlation_heatmap)
    ], style={"width": "96%", "margin": "auto", "padding": "10px"})
])

if __name__ == '__main__':
    app.run(debug=True)
