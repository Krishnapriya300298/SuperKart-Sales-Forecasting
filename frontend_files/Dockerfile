FROM python:3.11-slim

WORKDIR /app

# The dependencies are installed first
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# The Streamlit app is copied
COPY . .

# The backend is reached by its container name on the shared Docker network
ENV BACKEND_URL=http://backend:7860

# Streamlit runs on port 8501
EXPOSE 8501

# XSRF and CORS checks are turned off so that file upload works through the Codespaces forwarded URL
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", \
     "--server.enableXsrfProtection=false", "--server.enableCORS=false"]
