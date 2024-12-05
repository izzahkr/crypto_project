import streamlit as st
import pandas as pd
import psycopg2
import os
import plotly.express as px
import logging

# Database connection
def get_connection():
    try:
        logging.debug(f"Connecting to DB at {os.getenv('POSTGRES_HOST', 'crypto_project-postgres-1')}:{os.getenv('POSTGRES_PORT', '5432')}")
        return psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", "crypto_project-postgres-1"),  # Use the Postgres container name
            port=os.getenv("POSTGRES_PORT", "5432"),
            user=os.getenv("POSTGRES_USER", "postgres"),
            password=os.getenv("POSTGRES_PASSWORD", "postgres"),
            dbname=os.getenv("POSTGRES_DB", "crypto_db"),
        )
    except Exception as e:
        logging.error(f"Error connecting to the database: {e}")
        st.error("Failed to connect to the database. Please check the connection details.")
        return None


# Fetch data from database
@st.cache_data
def fetch_data():
    conn = get_connection()
    if conn is None:
        return pd.DataFrame()  # Return empty DataFrame if connection failed
    query = "SELECT * FROM crypto_data;"  # Ensure 'symbol' exists in this table
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# App layout
st.set_page_config(
    page_title="Crypto Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("📊 Crypto Market Dashboard")

# Show loading spinner
with st.spinner('Loading data...'):
    # Load data
    data = fetch_data()

# Debugging: Check columns
if data.empty:
    st.error("No data available. Please check your database connection or query.")
    st.stop()

# Debugging: Check columns of the data
st.write(data.columns)  # Check if 'symbol' column exists

# ===== Sidebar Filters =====
st.sidebar.header("Filters")

# Filter by Symbol
if "symbol" in data.columns:
    symbol_filter = st.sidebar.selectbox("Select Cryptocurrency", options=["All"] + data["symbol"].unique().tolist())
else:
    st.error("The 'symbol' column is missing in the data.")
    st.stop()

# Filter by Price Range
price_filter = st.sidebar.slider("Filter by Price Range", 0, int(data["current_price"].max()), (0, int(data["current_price"].max())))

# ===== Filtered Data =====
if symbol_filter != "All":
    filtered_data = data[(data["symbol"] == symbol_filter) & (data["current_price"].between(*price_filter))]
else:
    filtered_data = data[data["current_price"].between(*price_filter)]

# ===== Metrics (Cards) =====
st.markdown("## 📈 Market Overview")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Highest Price",
        value=f"${data['current_price'].max():,.2f}",
        delta=f"{data.loc[data['current_price'].idxmax(), 'name']}",
    )
with col2:
    st.metric(
        label="Total Market Cap",
        value=f"${data['market_cap'].sum():,}"
    )
with col3:
    st.metric(
        label="Total Volume",
        value=f"${data['total_volume'].sum():,}"
    )
with col4:
    st.metric(
        label="Number of Cryptos",
        value=f"{data['symbol'].nunique()} Coins"
    )

# ===== Visualizations =====
st.markdown("## 📊 Visualizations")

# Line chart for price trends
st.markdown("### 💹 Price Trends by Symbol")
if symbol_filter != "All":
    trend_data = filtered_data.sort_values(by="last_updated")
else:
    trend_data = data.sort_values(by="last_updated")

fig_line = px.line(
    trend_data,
    x="last_updated",
    y="current_price",
    title=f"Price Trend for {symbol_filter if symbol_filter != 'All' else 'All Cryptocurrencies'}",
    labels={"last_updated": "Date", "current_price": "Price (USD)"},
)
st.plotly_chart(fig_line, use_container_width=True)

# Bar chart for market cap comparison
st.markdown("### 📊 Market Cap Comparison")
fig_bar = px.bar(
    data.sort_values(by="market_cap", ascending=False).head(10),
    x="name",
    y="market_cap",
    text="market_cap",
    title="Top 10 Cryptocurrencies by Market Cap",
    labels={"market_cap": "Market Cap (USD)", "name": "Cryptocurrency"},
)
fig_bar.update_traces(texttemplate="$%{text:,}", textposition="outside")
st.plotly_chart(fig_bar, use_container_width=True)

# Pie chart for market share
st.markdown("### 🥧 Market Share by Symbol")
fig_pie = px.pie(
    data,
    names="name",
    values="market_cap",
    title="Market Share Distribution",
    labels={"market_cap": "Market Cap (USD)", "name": "Cryptocurrency"},
)
st.plotly_chart(fig_pie, use_container_width=True)

# ===== Data Table =====
st.markdown("### 📋 Top Cryptocurrencies")
if filtered_data.empty:
    st.warning("No data available for the selected filters.")
else:
    st.dataframe(filtered_data)

# ===== Footer =====
st.markdown("---")
st.markdown("📊 Built with ❤️ using Streamlit | Data Source: Airflow")

