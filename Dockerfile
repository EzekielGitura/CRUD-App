FROM python:3.9-slim

WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=app.main \
    FLASK_ENV=production

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories if they don't exist
RUN mkdir -p data instance

# Initialize the database
RUN flask init-db

# Expose port
EXPOSE 5000

# Set the entrypoint
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app.main:app"]