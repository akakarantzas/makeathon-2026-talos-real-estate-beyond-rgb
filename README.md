# Terrasset

Terrasset is a hyperspectral land screening app for comparing four Greek plots using EnMap data, NDVI, NDWI, and a simple investment score.

## Structure

```text
backend/   FastAPI analysis API
frontend/  Vite React app
data/      EnMap mosaics for the four plots
report/    Reference assets and project visuals
```

## Run

Install Python dependencies:

```powershell
pip install -r requirements.txt
```

Start the API:

```powershell
python -m uvicorn backend.main:app --reload --port 8001
```

Start the frontend:

```powershell
cd frontend
npm install
npm run dev
```
