"""ontology_app package."""

# re-export only the non‑UI submodules for convenience
from . import models, viz, storage

__all__ = ["models", "viz", "storage"]
