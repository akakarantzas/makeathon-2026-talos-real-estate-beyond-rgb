from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .analysis_adapter import PLOTS, list_plots, load_scene


app = FastAPI(title="Real Estate Beyond RGB API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5174", "http://127.0.0.1:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/plots")
def get_plots() -> list[dict]:
    return list_plots()


@app.get("/api/plots/{plot_name}")
def get_plot(plot_name: str) -> dict:
    if plot_name not in PLOTS:
        raise HTTPException(status_code=404, detail="Unknown plot")
    return load_scene(plot_name)
