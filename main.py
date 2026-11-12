"""MkDocs-macros entrypoint shim.

Implementation lives in ``src/``. This thin root module exists because
mkdocs-macros-plugin loads ``main.py`` from the project root by default.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

# Reloaded before each serve rebuild so edits in src/ replace the cached import.
_RELOAD_BEFORE_SRC = ("banner_lib", "humour_lib")


def _reload_imported(names: tuple[str, ...]) -> None:
    import importlib

    for name in names:
        module = sys.modules.get(name)
        if module is not None:
            importlib.reload(module)


def _load_src_main() -> ModuleType:
    src_dir = Path(__file__).resolve().parent / "src"
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))
    _reload_imported(_RELOAD_BEFORE_SRC)
    src_main = src_dir / "main.py"
    spec = importlib.util.spec_from_file_location("lupaxa_org_macros", src_main)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load macros module from {src_main}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["lupaxa_org_macros"] = module
    spec.loader.exec_module(module)
    return module


_MOD = _load_src_main()

# Expose the implementation module's public API on this shim (macros + tests).
define_env = _MOD.define_env
globals().update({name: getattr(_MOD, name) for name in dir(_MOD) if not name.startswith("__")})
