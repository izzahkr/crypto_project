FROM apache/airflow:2.7.1-python3.9

# Install additional dependencies
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

# Set environment variables for Airflow
ENV AIRFLOW_HOME=/opt/airflow
WORKDIR /opt/airflow

