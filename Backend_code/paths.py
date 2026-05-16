from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = Path(__file__).resolve().parent
DATA_DIR = BACKEND_DIR / "data"


def get_data_path(*parts: str) -> Path:
    if not DATA_DIR.exists():
        raise FileNotFoundError(
            "Canonical data directory not found. "
            f"Expected backend data at: {DATA_DIR}"
        )
    return DATA_DIR.joinpath(*parts)


def require_data_path(*parts: str) -> Path:
    path = get_data_path(*parts)
    if not path.exists():
        raise FileNotFoundError(f"Expected data path does not exist: {path}")
    return path
