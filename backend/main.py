from .adapter_loader import ensure_backend_code_on_path

ensure_backend_code_on_path()

from adapters.api import app, get_plot, get_plots  # noqa: E402,F401
