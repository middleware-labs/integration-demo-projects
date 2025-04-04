FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY load_generator.py .

# Run the load generator
CMD ["python", "load_generator.py"]
