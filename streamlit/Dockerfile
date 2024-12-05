FROM python:3.9

# Install dependencies
RUN apt-get update && apt-get install -y netcat-openbsd
RUN pip install --upgrade pip
RUN pip install streamlit psycopg2 pandas plotly
# Install PostgreSQL Client
RUN apt-get update && apt-get install -y postgresql-client


# Set working directory
WORKDIR /app

# Copy application files
COPY . /app

# Expose port for Streamlit
EXPOSE 8501

# Run Streamlit app
CMD ["streamlit", "run", "app_streamlit.py"]

