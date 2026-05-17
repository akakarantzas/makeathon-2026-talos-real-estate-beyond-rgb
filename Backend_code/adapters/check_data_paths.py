"""Smoke-check canonical backend data path resolution."""

from Backend_code.paths import BACKEND_DIR, DATA_DIR, REPO_ROOT, require_data_path


def main() -> None:
    if not REPO_ROOT.exists():
        raise FileNotFoundError(f"Repository root does not exist: {REPO_ROOT}")
    if not BACKEND_DIR.exists():
        raise FileNotFoundError(f"Backend directory does not exist: {BACKEND_DIR}")
    if not DATA_DIR.exists():
        raise FileNotFoundError(f"Backend data directory does not exist: {DATA_DIR}")

    expected_plot_dir = require_data_path("Arkadia")

    print(f"Repository root: {REPO_ROOT}")
    print(f"Backend directory: {BACKEND_DIR}")
    print(f"Backend data directory: {DATA_DIR}")
    print(f"Verified expected data subfolder: {expected_plot_dir}")


if __name__ == "__main__":
    main()
