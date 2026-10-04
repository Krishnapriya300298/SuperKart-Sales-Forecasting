# A small Python image is used as the base
FROM python:3.11-slim

# All the app files are kept in /app inside the container
WORKDIR /app

# libgomp1 is needed by XGBoost
RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# The dependencies are installed first so that this layer is cached
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# The app code and the saved model are copied
COPY . .

# The API runs on port 7860
EXPOSE 7860

# Gunicorn is used to serve the Flask app (app.py -> superkart_api)
CMD ["gunicorn", "--workers", "2", "--bind", "0.0.0.0:7860", "app:superkart_api"]
