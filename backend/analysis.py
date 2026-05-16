from .adapter_loader import ensure_backend_code_on_path

ensure_backend_code_on_path()

from adapters.analysis_adapter import *  # noqa: E402,F403
