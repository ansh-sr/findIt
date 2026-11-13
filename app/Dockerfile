FROM python:3.11-slim

WORKDIR /app

# Install dependencies required for building/linking PostgreSQL client libraries
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Copy dependency list and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application code
COPY . .

# Expose internal Flask port
EXPOSE 5000

# Run the app
CMD ["python", "app.py"]