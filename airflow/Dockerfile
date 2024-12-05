# Gunakan image dasar Airflow
FROM apache/airflow:2.3.0

# Pindahkan ke pengguna airflow sebelum menjalankan pip install
USER airflow

# Install dependensi tambahan
RUN pip install --no-cache-dir psycopg2-binary requests

# Menyalin file DAG ke dalam container
COPY ./dags /opt/airflow/dags

# Menyalin file konfigurasi airflow.cfg jika ada
COPY airflow.cfg /opt/airflow/airflow.cfg

# Pastikan Airflow berjalan dengan benar saat container dijalankan
CMD ["bash", "-c", "airflow db init && airflow webserver"]

