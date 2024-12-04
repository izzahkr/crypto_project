FROM python:3.9-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && apt-get clean

WORKDIR /app

# Copy application code
COPY app.py /app/
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "app.py"]

