from .adapter_loader import ensure_backend_code_on_path

ensure_backend_code_on_path()

from adapters.check_data_paths import main  # noqa: E402


if __name__ == "__main__":
    main()
