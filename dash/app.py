import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import psycopg2
import pandas as pd

# Inisialisasi aplikasi Dash
app = dash.Dash(__name__)

# Fungsi untuk mengambil data dari PostgreSQL
def get_data_from_postgres():
    conn = psycopg2.connect(
        dbname="crypto_db", user="postgres", password="postgres", host="localhost"
    )
    query = "SELECT * FROM crypto_data ORDER BY last_updated DESC LIMIT 10;"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Layout Dash
app.layout = html.Div([
    html.H1('Cryptocurrency Dashboard'),
    dcc.Graph(
        id='crypto-price-graph',
        figure={
            'data': [
                go.Bar(
                    x=get_data_from_postgres()['name'],
                    y=get_data_from_postgres()['current_price'],
                    name='Price (USD)',
                    marker={'color': 'green'}
                )
            ],
            'layout': go.Layout(
                title='Top 10 Cryptocurrency Prices',
                xaxis={'title': 'Cryptocurrency'},
                yaxis={'title': 'Price (USD)'}
            )
        }
    )
])

# Menjalankan server Dash
if __name__ == '__main__':
    app.run_server(debug=True)
