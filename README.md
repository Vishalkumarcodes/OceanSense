# OceanSense — Complete Project

This repository contains the OceanSense website frontend, a FastAPI backend, and a Streamlit analytics app.

See `backend/.env.example` for environment variables. Create a Postgres DB named `oceandatabase` and update `DATABASE_URL`.

Run backend:

```
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Serve frontend (simple):
```
python -m http.server 5500 --directory frontend
```

Run Streamlit:
```
streamlit run streamlit_app/streamlit_app.py
```
