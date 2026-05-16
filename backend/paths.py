from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_CODE_DIR = REPO_ROOT / "Backend Code"
BACKEND_CODE_DATA_DIR = BACKEND_CODE_DIR / "data"


def get_data_path(*parts: str) -> Path:
    if not BACKEND_CODE_DATA_DIR.exists():
        raise FileNotFoundError(
            "Canonical data directory not found. "
            f"Expected Backend Code data at: {BACKEND_CODE_DATA_DIR}"
        )
    return BACKEND_CODE_DATA_DIR.joinpath(*parts)
