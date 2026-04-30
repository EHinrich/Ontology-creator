"""UI re-exports: import GUI classes from the refactored module.

Note: `Ontology1.py` no longer runs the QApplication at import-time;
it only defines the widgets and a `main()` entrypoint.
"""
from Ontology import (
    Window,
    LoginWindow,
    AddClassWindow,
    AddElemWindow,
    DelClassWindow,
    DelElemWindow,
    AddRelClassesWindow,
    AddRelElemWindow,
    AddValueWindow,
    SumWindow,
    AddNodeWindow,
)

__all__ = [
    "Window",
    "LoginWindow",
    "AddClassWindow",
    "AddElemWindow",
    "DelClassWindow",
    "DelElemWindow",
    "AddRelClassesWindow",
    "AddRelElemWindow",
    "AddValueWindow",
    "SumWindow",
    "AddNodeWindow",
    "WindowSchemeForSum",
]
