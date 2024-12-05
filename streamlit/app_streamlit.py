import streamlit as st
import pandas as pd
import psycopg2
import os
import plotly.express as px

# Database connection
def get_connection():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "postgres"),
        dbname=os.getenv("POSTGRES_DB", "crypto_db"),
    )

# Fetch data from database
@st.cache_data
def fetch_data():
    conn = get_connection()
    query = "SELECT * FROM crypto_data;"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# App layout and navigation
st.set_page_config(
    page_title="Crypto Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Sidebar for navigation
st.sidebar.header("Navigation")
page = st.sidebar.radio("Select Page", ["Home", "Visualization"])

if page == "Home":
    # Center the title and apply styles
    st.markdown("""
        <h1 style='text-align: center; color: #1E90FF; font-family: Arial; border: 2px solid #00BFFF; padding: 10px; border-radius: 10px; background-color: rgba(255, 255, 255, 0.1);'>CRYPTO MARKET DASHBOARD</h1>
        <p style='text-align: left; color: #FFFFFF; font-family: Arial; font-size: 20px;'>
    \nWelcome to the Crypto Market Dashboard! This platform provides comprehensive insights into the cryptocurrency market, 
    allowing you to visualize trends, compare market caps, and make informed investment decisions.
    </p>
    """, unsafe_allow_html=True)

    # Add an image
    st.image("/home/3323600030_Aulia/crypto_project/streamlit/crypto.jpg", use_container_width=True)

    # Add visualization explanation and purpose below the image
    st.markdown("""
        <p style='text-align: left; color: #FFFFFF; font-family: Arial; font-size: 20px;'>
        Explore various visualizations that reveal crucial insights, including price trends over time, market cap comparisons among top cryptocurrencies, 
        and market share distributions. These tools are designed to empower your investment strategies and help you make data-driven decisions in the fast-paced crypto market.
        </p>
        
        <h2 style='color: #FFD700; font-family: Arial;'>Purpose of Visualizations</h2>
        <ul style='text-align: left; color: #FFFFFF; font-family: Arial; font-size: 16px;'>
            <li><strong>Price Trends:</strong> Understand how cryptocurrency prices fluctuate over time, helping you identify potential buying or selling opportunities.</li>
            <li><strong>Market Cap Comparison:</strong> Compare the market capitalizations of the top cryptocurrencies to gauge their relative strength and investment potential.</li>
            <li><strong>Market Share Distribution:</strong> Visualize the market share of different cryptocurrencies to comprehend their dominance in the market.</li>
        </ul>
    """, unsafe_allow_html=True)

elif page == "Visualization":
    # Load data
    data = fetch_data()

    # ===== Sidebar Filters =====
    st.sidebar.header("Filters")

    # Filter by Symbol
    symbol_filter = st.sidebar.selectbox("Select Cryptocurrency", options=["All"] + data["symbol"].unique().tolist())

    # Filter by Price Range
    price_filter = st.sidebar.slider("Filter by Price Range", 0, int(data["current_price"].max()), (0, int(data["current_price"].max())))

    # ===== Filtered Data =====
    if symbol_filter != "All":
        filtered_data = data[(data["symbol"] == symbol_filter) & (data["current_price"].between(*price_filter))]
    else:
        filtered_data = data[data["current_price"].between(*price_filter)]

    # Format the relevant columns as strings
    columns_to_format = ['current_price', 'market_cap', 'total_volume', 'circulating_supply']
    for column in columns_to_format:
        filtered_data[column] = filtered_data[column].apply(lambda x: f"{x:,.0f}")

    # ===== Visualizations =====
    st.markdown("""
        <h2 style='text-align: left; color: #FF69B4; font-family: "Playfair Display", serif;'>✨ VISUALIZATION ✨</h2>
    """, unsafe_allow_html=True)

    # ===== Metrics (Cards) =====
    st.markdown("## 📈 Market Overview")

    # Create a container to center the metrics
    with st.container():
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
                value=f"${data['market_cap'].sum():,.1f}"
            )
        with col3:
            st.metric(
                label="Total Volume",
                value=f"${data['total_volume'].sum():,.1f}"
            )
        with col4:
            st.metric(
                label="Number of Cryptos",
                value=f"{data['symbol'].nunique()} Coins"
            )

    # ===== Data Table =====
    st.markdown("""
        <h3 style='text-align: center; color: #FFD700; font-family: Arial;'>📋 Top Cryptocurrencies</h3>
        <style>
            .dataframe {
                border-collapse: collapse;
                width: 100%; 
                font-size: 20px; 
                color: #FFFFFF; 
            }
            .dataframe th, .dataframe td {
                border: 1px solid #FFD700; 
                padding: 10px; 
                text-align: center; 
            }
            .dataframe th {
                background-color: #333333; 
            }
            .dataframe tr:nth-child(even) {
                background-color: #444444; 
            }
            .dataframe tr:hover {
                background-color: #555555; 
            }
        </style>
        """ + filtered_data.style.set_table_attributes('class="dataframe"').to_html() + """
    """, unsafe_allow_html=True)

    # Create a layout for the visualizations
    col1, col2 = st.columns(2)

    # Bar chart for market cap comparison
    with col1:
        st.markdown("""
            <h3 style='text-align: left; color: #FFD700; font-family: Arial;'>📊 Market Cap Comparison</h3>
        """, unsafe_allow_html=True)
        fig_bar = px.bar(
            data.sort_values(by="market_cap", ascending=False).head(10),
            x="name",
            y="market_cap",
            text="market_cap",
            title="Top 10 Cryptocurrencies by Market Cap",
            labels={"market_cap": "Market Cap (USD)", "name": "Cryptocurrency"},
            template="plotly_dark"
        )
        fig_bar.update_traces(texttemplate="$%{text:,.0f}", textposition="outside")
        fig_bar.update_layout(height=400)
        st.plotly_chart(fig_bar, use_container_width=True)

    # Pie chart for market share
    with col2:
        st.markdown("""
            <h3 style='text-align: left; color: #FFD700; font-family: Arial;'>🥧 Market Share by Symbol</h3>
        """, unsafe_allow_html=True)
        fig_pie = px.pie(
            data,
            names="name",
            values="market_cap",
            title="Market Share Distribution",
            labels={"market_cap": "Market Cap (USD)", "name": "Cryptocurrency"},
            template="plotly_dark"
        )
        fig_pie.update_traces(textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)

    # Line chart for price trends
    st.markdown("""
        <h3 style='text-align: left; color: #FFD700; font-family: Arial;'>💹 Price Trends by Symbol</h3>
    """, unsafe_allow_html=True)
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
        template="plotly_dark"
    )
    fig_line.update_layout(height=400)
    st.plotly_chart(fig_line, use_container_width=True)

# ===== Footer =====
st.markdown("---")
st.markdown("📊 Built with ❤️ using Streamlit | Data Source: Airflow")