"""Smoke-check canonical backend data path resolution."""

from .paths import BACKEND_CODE_DATA_DIR, BACKEND_CODE_DIR, REPO_ROOT, require_data_path


def main() -> None:
    if not REPO_ROOT.exists():
        raise FileNotFoundError(f"Repository root does not exist: {REPO_ROOT}")
    if not BACKEND_CODE_DIR.exists():
        raise FileNotFoundError(f"Backend Code directory does not exist: {BACKEND_CODE_DIR}")
    if not BACKEND_CODE_DATA_DIR.exists():
        raise FileNotFoundError(f"Backend Code data directory does not exist: {BACKEND_CODE_DATA_DIR}")

    expected_plot_dir = require_data_path("Arkadia")

    print(f"Repository root: {REPO_ROOT}")
    print(f"Backend Code directory: {BACKEND_CODE_DIR}")
    print(f"Backend Code data directory: {BACKEND_CODE_DATA_DIR}")
    print(f"Verified expected data subfolder: {expected_plot_dir}")


if __name__ == "__main__":
    main()
