from pathlib import Path
import sys


def ensure_backend_code_on_path() -> None:
    backend_code_dir = Path(__file__).resolve().parents[1] / "Backend Code"
    backend_code_str = str(backend_code_dir)
    if backend_code_str not in sys.path:
        sys.path.insert(0, backend_code_str)
