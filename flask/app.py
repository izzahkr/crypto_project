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
    try:
        conn = psycopg2.connect(
            dbname="crypto_db", user="postgres", password="postgres", host="postgres"
        )
        query = "SELECT * FROM crypto_data ORDER BY market_cap DESC;"
        df = pd.read_sql(query, conn)
        conn.close()
        print("Data fetched successfully")
        return df
    except Exception as e:
        print(f"Error fetching data: {e}")
        return pd.DataFrame()  # Return empty DataFrame on error

# Initial data
crypto_data = get_data_from_postgres()
print(crypto_data.head())  # Debugging

# Dash layout
app.layout = html.Div(
    style={'padding': '20px', 'backgroundColor': '#1E1E1E'},
    children=[
        html.H1('Cryptocurrency Dashboard', style={'textAlign': 'center', 'color': '#FFD700', 'fontSize': '36px'}),
        
        # Dropdown filter
        dcc.Dropdown(
            id='crypto-dropdown',
            options=[{'label': row['name'], 'value': row['name']} for _, row in crypto_data.iterrows()],
            value=crypto_data['name'].iloc[0] if not crypto_data.empty else None,  # Default to the top cryptocurrency
            clearable=False,
            style={
                'width': '30%',
                'margin': '20px auto',
                'backgroundColor': '#3A3A3A',  # Dark background
                'color': '#3A3A3A',  # White text
                'border': '1px solid #444444',
                'fontSize': '16px',
                'fontFamily': 'Arial, sans-serif',  # Specific font family
            },
            className='custom-dropdown',  # Add class for additional styling
        ),
        
        # Metric cards
        html.Div(id='metric-cards', style={'display': 'grid', 'gridTemplateColumns': 'repeat(auto-fit, minmax(250px, 1fr))', 'gap': '20px', 'marginBottom': '20px'}),

        # Table for top 5 cryptocurrencies
        html.Div(id='top-5-table-container', style={'marginTop': '20px', 'marginBottom': '20px'}),

        # Create a container for the bar chart and pie chart
        html.Div(
            style={'marginTop': '20px'},
            children=[
                html.Div(
                    style={'display': 'flex', 'justifyContent': 'space-between'},
                    children=[
                        dcc.Graph(id='price-volume-graph', style={'height': '400px', 'width': '48%'}),
                        dcc.Graph(id='market-cap-pie', style={'height': '400px', 'width': '48%'})
                    ]
                ),
            ]
        ),
    ]
)

@app.callback(
    [Output('price-volume-graph', 'figure'),
     Output('market-cap-pie', 'figure'),
     Output('metric-cards', 'children'),
     Output('top-5-table-container', 'children')],
    [Input('crypto-dropdown', 'value')]
)
def update_graphs(selected_crypto):
    if selected_crypto is None:
        return {}, {}, [], html.Div()  # Return empty if no selection

    print(f"Selected Crypto: {selected_crypto}")  # Debugging
    selected_data = crypto_data[crypto_data['name'] == selected_crypto].iloc[0]
    print(f"Selected Data: {selected_data}")  # Debugging

    # Metric cards
    metric_cards = [
        html.Div([
            html.H3(f"${selected_data['current_price']:,.2f}", style={'color': '#FFFFFF', 'fontSize': '24px'}),
            html.P("Current Price", style={'color': '#FFFFFF'}),
        ], style={'backgroundColor': '#444444', 'padding': '20px', 'borderRadius': '10px', 'textAlign': 'center'}),
        
        html.Div([
            html.H3(f"${selected_data['market_cap']:,.2f}", style={'color': '#FFFFFF', 'fontSize': '24px'}),
            html.P("Market Cap", style={'color': '#FFFFFF'}),
        ], style={'backgroundColor': '#444444', 'padding': '20px', 'borderRadius': '10px', 'textAlign': 'center'}),
        
        html.Div([
            html.H3(f"${selected_data['total_volume']:,.2f}", style={'color': '#FFFFFF', 'fontSize': '24px'}),
            html.P("Total Volume", style={'color': '#FFFFFF'}),
        ], style={'backgroundColor': '#444444', 'padding': '20px', 'borderRadius': '10px', 'textAlign': 'center'}),
    ]

    # Create price and volume bar graph
    price_volume_fig = {
        'data': [
            go.Bar(
                x=['Current Price', 'Market Cap', 'Total Volume'], 
                y=[selected_data['current_price'], selected_data['market_cap'], selected_data['total_volume']],
                marker=dict(color='#00C896')
            )
        ],
        'layout': go.Layout(
            title=f'{selected_crypto} Metrics',
            xaxis=dict(title='Metrics', titlefont=dict(color='#FFFFFF')),
            yaxis=dict(title='Values (in USD)', titlefont=dict(color='#FFFFFF')),
            plot_bgcolor='#2E2E2E',
            paper_bgcolor='#2E2E2E',
            font=dict(color='#FFFFFF')
        )
    }

    # Create pie chart for circulating supply
    pie_fig = {
        'data': [
            go.Pie(
                labels=['Circulating Supply', 'Remaining Supply'],
                values=[selected_data['circulating_supply'], 21000000 - selected_data['circulating_supply']],
                marker=dict(colors=['#FFC300', '#0073FF']),
                textinfo='label+percent'
            )
        ],
        'layout': go.Layout(
            title=f'{selected_crypto} Supply Distribution',
            plot_bgcolor='#2E2E2E',
            paper_bgcolor='#2E2E2E',
            font=dict(color='#FFFFFF')
        )
    }

    # Create table for top 5 cryptocurrencies
    top_5_data = crypto_data.head(5)
    table_fig = go.Figure(data=[go.Table(
        header=dict(values=['Name', 'Symbol', 'Current Price', 'Market Cap', 'Total Volume'],
                    fill_color='#444444',  # Darker header
                    font=dict(color='#FFFFFF', size=12),
                    align='left'),
        cells=dict(values=[top_5_data['name'], top_5_data['symbol'], top_5_data['current_price'], 
                           top_5_data['market_cap'], top_5_data['total_volume']],
                   fill_color='#333333',  # Darker cell background
                   font=dict(color='#FFFFFF', size=12),
                   align='left'))
    ])
    
    table_fig.update_layout(
        height=300,
        paper_bgcolor='#2E2E2E',
        font=dict(color='#FFFFFF')
    )

    # Display the top 5 table as HTML inside a container with title
    top_5_table = html.Div([
        html.Div([
            html.H3("Top 5 Cryptocurrencies", style={'color': '#FFFFFF', 'textAlign': 'center', 'padding': '10px'}),
        ], style={'backgroundColor': '#444444', 'borderRadius': '8px', 'marginBottom': '15px'}),
        dcc.Graph(figure=table_fig)
    ], style={'padding': '10px', 'backgroundColor': '#1E1E1E', 'borderRadius': '10px'})

    return price_volume_fig, pie_fig, metric_cards, top_5_table

@server.route('/')
def index():
    return render_template('index.html')

@server.route('/dashboard/')
def dashboard():
    return render_template('dashboard.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

