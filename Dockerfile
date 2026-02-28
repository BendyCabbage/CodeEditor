FROM python:3.13-slim

WORKDIR /app

# Install dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/server/ .

# Fly.io expects port 8080
ENV PORT=8080

EXPOSE 8080

CMD ["python", "app.py"]
