from airflow import DAG
from airflow.providers.http.sensors.http import HttpSensor
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from datetime import timedelta
import requests
import psycopg2
import json
import os

# Konfigurasi DAG
dag = DAG(
    'crypto_data_pipeline',
    default_args={
        'owner': 'airflow',
        'retries': 3,
        'retry_delay': timedelta(minutes=5),
    },
    description='DAG untuk mengambil data cryptocurrency dari CoinGecko',
    schedule_interval='@hourly',
    start_date=days_ago(1),
    catchup=False,
)

# Path file sementara
TEMP_FILE_PATH = "/tmp/crypto_data.json"

# Fungsi untuk mengambil data dari CoinGecko
def get_crypto_data():
    url = 'https://api.coingecko.com/api/v3/coins/markets'
    params = {
        'vs_currency': 'usd',
        'ids': 'bitcoin,ethereum,litecoin,tether,binancecoin',
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise ValueError(f"Request failed with status code {response.status_code}: {response.text}")

    data = response.json()
    if not data:
        raise ValueError("No data received from API.")

    # Simpan data ke file sementara
    with open(TEMP_FILE_PATH, 'w') as f:
        json.dump(data, f)

# Fungsi untuk menyimpan data ke PostgreSQL
def save_to_postgres():
    # Membaca data dari file sementara
    with open(TEMP_FILE_PATH, 'r') as f:
        data = json.load(f)

    # Koneksi ke PostgreSQL
    conn = psycopg2.connect(
        dbname="crypto_db", user="postgres", password="postgres", host="crypto_project-postgres-1"
    )
    cursor = conn.cursor()

    for item in data:
        cursor.execute(
            """INSERT INTO crypto_data (name, symbol, current_price, market_cap, total_volume, circulating_supply, last_updated)
            VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (
                item['name'],
                item['symbol'],
                item['current_price'],
                item['market_cap'],
                item['total_volume'],
                item['circulating_supply'],
                item['last_updated'],  # Format datetime ini harus sesuai dengan skema database
            )
        )
    conn.commit()
    cursor.close()
    conn.close()

    # Hapus file sementara setelah data disimpan
    if os.path.exists(TEMP_FILE_PATH):
        os.remove(TEMP_FILE_PATH)

# Task untuk memeriksa koneksi ke CoinGecko API
check_api_connection = HttpSensor(
    task_id='check_api_connection',
    http_conn_id='coin_gecko_api',
    endpoint='api/v3/coins/markets',
    request_params={'vs_currency': 'usd'},
    poke_interval=30,
    timeout=300,
    mode='poke',  # Gunakan mode poke agar tidak membebani sistem
    dag=dag,
)

# Task untuk mengambil data cryptocurrency
fetch_data_task = PythonOperator(
    task_id='fetch_crypto_data',
    python_callable=get_crypto_data,
    dag=dag,
)

# Task untuk menyimpan data ke PostgreSQL
save_data_task = PythonOperator(
    task_id='save_to_postgres',
    python_callable=save_to_postgres,
    dag=dag,
)

# Set urutan tugas
check_api_connection >> fetch_data_task >> save_data_task

