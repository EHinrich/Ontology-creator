"""ontology_app package.

This __init__ no longer imports the UI submodule automatically because
``Ontology1`` itself imports the package (for ``models``/``viz``) and
re-exporting the GUI classes triggered a circular import.  Clients who need
the widgets can import them explicitly from ``ontology_app.ui`` or continue to
import directly from ``Ontology1``.
"""

# re-export only the non‑UI submodules for convenience
from . import models, viz, storage

__all__ = ["models", "viz", "storage"]
