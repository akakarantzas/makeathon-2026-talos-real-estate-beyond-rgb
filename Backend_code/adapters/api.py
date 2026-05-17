import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .analysis_adapter import PLOTS, list_plots, load_pipeline_payload, load_scene


DEFAULT_CORS_ORIGINS = ["http://localhost:5174", "http://127.0.0.1:5174"]


def get_cors_origins() -> list[str]:
    configured_origins = os.getenv("CORS_ORIGINS")
    if not configured_origins:
        return DEFAULT_CORS_ORIGINS
    return [origin.strip() for origin in configured_origins.split(",") if origin.strip()]


app = FastAPI(title="Real Estate Beyond RGB API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/plots")
def get_plots() -> list[dict]:
    return list_plots()


@app.get("/api/meta")
def get_meta() -> dict:
    return load_pipeline_payload().get("project_meta", {})


@app.get("/api/plots/{plot_name}")
def get_plot(plot_name: str) -> dict:
    if plot_name not in PLOTS:
        raise HTTPException(status_code=404, detail="Unknown plot")
    return load_scene(plot_name)
