from flask import Flask, render_template
from dash import Dash, dcc, html, Input, Output
import plotly.graph_objs as go
import psycopg2
import pandas as pd

# Initialize Flask app
server = Flask(__name__)

# Initialize Dash app
app = Dash(__name__, server=server, url_base_pathname='/dashboard/')

# Function to fetch data from PostgreSQL
def get_data_from_postgres():
    conn = psycopg2.connect(
        dbname="crypto_db", user="postgres", password="postgres", host="localhost"
    )
    query = "SELECT * FROM crypto_data ORDER BY market_cap DESC;"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Initial data
crypto_data = get_data_from_postgres()

# Dash layout
app.layout = html.Div(
    style={'padding': '20px', 'backgroundColor': '#1E1E1E'},
    children=[
        html.H1('Cryptocurrency Dashboard', style={'textAlign': 'center', 'color': '#FFD700', 'fontSize': '36px'}),
        dcc.Dropdown(
            id='crypto-dropdown',
            options=[{'label': row['name'], 'value': row['name']} for _, row in crypto_data.iterrows()],
            value=crypto_data['name'].iloc[0],  # Default to the top cryptocurrency
            clearable=False,
            style={
                'width': '60%',
                'margin': '20px auto',
                'backgroundColor': '#3A3A3A',
                'color': '#FFFFFF',
                'border': '1px solid #444444',
                'fontSize': '16px'
            }
        ),

        # Create a grid layout for metric cards
        html.Div(id='metric-cards', style={'display': 'grid', 'gridTemplateColumns': 'repeat(auto-fit, minmax(250px, 1fr))', 'gap': '20px', 'marginBottom': '20px'}),
        
        # Create a grid layout for charts
        html.Div(style={'display': 'grid', 'gridTemplateColumns': '1fr 1fr', 'gap': '20px'}, children=[
            dcc.Graph(id='price-volume-graph'),
            dcc.Graph(id='market-cap-pie'),
        ]),
        
        # Top 5 cryptocurrencies table
        dcc.Graph(id='top-5-table', style={'marginTop': '20px'})
    ]
)

@app.callback(
    [Output('price-volume-graph', 'figure'),
     Output('market-cap-pie', 'figure'),
     Output('metric-cards', 'children'),
     Output('top-5-table', 'figure')],
    [Input('crypto-dropdown', 'value')]
)
def update_graphs(selected_crypto):
    selected_data = crypto_data[crypto_data['name'] == selected_crypto].iloc[0]

    # Metric cards in grid layout
    metric_cards = [
        html.Div([
            html.H3(f"${selected_data['current_price']:,.2f}", style={'color': '#FFFFFF', 'fontSize': '24px'}),
            html.P("Current Price", style={'color': '#FFFFFF'}),
        ], style={'backgroundColor': '#444444', 'padding': '20px', 'borderRadius': '10px', 'textAlign': 'center', 'transition': '0.3s', 'cursor': 'pointer', 'boxShadow': '0 4px 8px rgba(0,0,0,0.2)'}),
        
        html.Div([
            html.H3(f"${selected_data['market_cap']:,.2f}", style={'color': '#FFFFFF', 'fontSize': '24px'}),
            html.P("Market Cap", style={'color': '#FFFFFF'}),
        ], style={'backgroundColor': '#444444', 'padding': '20px', 'borderRadius': '10px', 'textAlign': 'center', 'transition': '0.3s', 'cursor': 'pointer', 'boxShadow': '0 4px 8px rgba(0,0,0,0.2)'}),
        
        html.Div([
            html.H3(f"${selected_data['total_volume']:,.2f}", style={'color': '#FFFFFF', 'fontSize': '24px'}),
            html.P("Total Volume", style={'color': '#FFFFFF'}),
        ], style={'backgroundColor': '#444444', 'padding': '20px', 'borderRadius': '10px', 'textAlign': 'center', 'transition': '0.3s', 'cursor': 'pointer', 'boxShadow': '0 4px 8px rgba(0,0,0,0.2)'}),
    ]

    # Create price and volume bar graph
    price_volume_fig = {
        'data': [
            go.Bar(
                x=['Current Price', 'Market Cap', 'Total Volume'], 
                y=[selected_data['current_price'], selected_data['market_cap'], selected_data['total_volume']],
                marker=dict(color='#00C896')  # Consistent color
            )
        ],
        'layout': go.Layout(
            title=f'{selected_crypto} Metrics',
            xaxis=dict(
                title='Metrics',
                titlefont=dict(color='#FFFFFF'),
                showline=True,
                linecolor='white',
                zeroline=True,
                zerolinecolor='white',
            ),
            yaxis=dict(
                title='Values (in USD)',
                titlefont=dict(color='#FFFFFF'),
                showline=True,
                linecolor='white',
                zeroline=True,
                zerolinecolor='white',
            ),
            plot_bgcolor='#2E2E2E',
            paper_bgcolor='#2E2E2E',
            font=dict(color='#FFFFFF'),
            margin=dict(l=40, r=40, t=40, b=40),
            xaxis_tickangle=-45,
            showlegend=False
        )
    }

    # Create pie chart for circulating supply
    pie_fig = {
        'data': [
            go.Pie(
                labels=['Circulating Supply', 'Remaining Supply'],
                values=[selected_data['circulating_supply'], 21000000 - selected_data['circulating_supply']],
                marker=dict(colors=['#FFC300', '#0073FF']),
                textinfo='label+percent',
                hoverinfo='label+percent'
            )
        ],
        'layout': go.Layout(
            title=f'{selected_crypto} Supply Distribution',
            plot_bgcolor='#2E2E2E',
            paper_bgcolor='#2E2E2E',
            font=dict(color='#FFFFFF'),
            margin=dict(t=40)
        )
    }

    # Create table for top 5 cryptocurrencies
    top_5_data = crypto_data.head(5)
    table_fig = go.Figure(data=[go.Table(
        header=dict(values=['Name', 'Symbol', 'Current Price', 'Market Cap', 'Total Volume'],
                    fill_color='#444444',
                    font=dict(color='#FFFFFF', size=12),
                    align='left'),
        cells=dict(values=[top_5_data['name'], top_5_data['symbol'], top_5_data['current_price'], 
                           top_5_data['market_cap'], top_5_data['total_volume']],
                   fill_color='#3A3A3A',
                   font=dict(color='#FFFFFF', size=12),
                   align='left'))
    ])
    
    table_fig.update_layout(
        height=300,
        paper_bgcolor='#2E2E2E',
        font=dict(color='#FFFFFF')
    )

    return price_volume_fig, pie_fig, metric_cards, table_fig

@server.route('/')
def index():
    return render_template('index.html')

@server.route('/dashboard/')
def dashboard():
    return render_template('dashboard.html')

if __name__ == '__main__':
    server.run(debug=True)
