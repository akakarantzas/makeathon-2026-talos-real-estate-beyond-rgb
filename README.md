# Terrasset

Terrasset is a hyperspectral land screening app for comparing four Greek plots using EnMap data, NDVI, NDWI, and a simple investment score.

## Structure

```text
Backend_code/  Backend implementation and canonical EnMap data
frontend/      Vite React app
report/        Reference assets and project visuals
```

## Quick start on Windows

1. Double-click `setup.bat` once.
2. Double-click `run_app.bat`.
3. Terrasset opens automatically in your browser.

## Manual local run

From the repository root, install Python dependencies:

```powershell
python -m pip install -r requirements.txt
```

In one terminal, start the API:

```powershell
python -m uvicorn Backend_code.adapters.api:app --reload --port 8001
```

In a second terminal, start the frontend:

```powershell
cd frontend
npm install
npm run dev
```
