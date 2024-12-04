CREATE TABLE IF NOT EXISTS crypto_data (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    symbol VARCHAR(50),
    current_price FLOAT,
    market_cap FLOAT,
    total_volume FLOAT,
    circulating_supply FLOAT,
    last_updated TIMESTAMP
);
