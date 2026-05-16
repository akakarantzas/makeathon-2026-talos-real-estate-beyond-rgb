# Terrasset

Terrasset is a hyperspectral land screening app for comparing four Greek plots using EnMap data, NDVI, NDWI, and a simple investment score.

## Structure

```text
Backend_code/  Backend implementation and canonical EnMap data
frontend/      Vite React app
report/        Reference assets and project visuals
```

## Run

Install Python dependencies:

```powershell
pip install -r requirements.txt
```

Start the API:

```powershell
python -m uvicorn Backend_code.adapters.api:app --reload --port 8001
```

Start the frontend:

```powershell
cd frontend
npm install
npm run dev
```
