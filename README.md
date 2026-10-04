# SuperKart Sales Forecasting - Containerized Deployment

This repository contains the Flask backend (model API) and the Streamlit frontend
for the SuperKart sales forecasting model.

```
backend_files/   Flask API + saved model (port 7860)
frontend_files/  Streamlit UI (port 8501)
Batch_Data_SuperKart.csv  sample file for batch prediction
```

## Run in GitHub Codespaces

```bash
# Option A: one script does everything (it also runs automatically when the Codespace starts)
bash start_app.sh

# Option B: the same steps by hand
# 1. Build the images
docker build -t superkart-backend ./backend_files
docker build -t superkart-frontend ./frontend_files

# 2. Create a shared network so the frontend can reach the backend by name
docker network create superkart-app-network

# 3. Start both containers
docker run -d --name backend  --network superkart-app-network -p 7860:7860 superkart-backend
docker run -d --name frontend --network superkart-app-network -p 8501:8501 superkart-frontend
```

Then open the **Ports** tab, set ports **7860** and **8501** to **Public**, and open the
forwarded URL of port 8501 to use the app.

## API

| Method | Endpoint | Body |
|---|---|---|
| GET  | `/` | - |
| POST | `/v1/predict` | JSON with the 10 features |
| POST | `/v1/predictbatch` | multipart form, CSV in field `file` |
