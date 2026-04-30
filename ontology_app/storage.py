"""Simple storage layer for ontology application.

Currently only supports a rudimentary user table used for login.  The
implementation wraps Qt's QSQLITE driver to match the original code; switching
to plain ``sqlite3`` would be straightforward if the GUI dependency is
unwanted.
"""
from typing import Optional
import os
from PyQt5.QtSql import QSqlDatabase, QSqlQuery

_db = None


def init_db(db_path: Optional[str] = None) -> QSqlDatabase:
    """Initialize and return the global database connection.

    If ``db_path`` is not provided a default under ``./data/q1364188.db`` is
    used, matching the previous hard‑coded location.  The function is
    idempotent, subsequent calls return the same connection object.
    """
    global _db
    if _db is not None:
        return _db
    if db_path is None:
        cwd = os.getcwd()
        db_path = os.path.join(cwd, "data", "q1364188.db")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    _db = QSqlDatabase.addDatabase("QSQLITE")
    _db.setDatabaseName(db_path)
    if not _db.open():
        raise RuntimeError(f"Failed to open database at {db_path}")
    query = QSqlQuery()
    query.exec_("create table if not exists user (id integer, user_name string, password string);")
    # ensure default admin exists (ignore errors if duplicate)
    query.exec_("insert or ignore into user (id, user_name, password) values (0, 'admin', '123' );")
    return _db


def check_user(username: str, password: str) -> bool:
    """Return ``True`` if ``username``/``password`` match the database.

    The real implementation should use prepared statements to avoid SQL
    injection; this simple version mirrors the behaviour of the original demo
    code where input is not sanitised.
    """
    if _db is None:
        init_db()
    query = QSqlQuery()
    query.exec_(f"select password from user where user_name='{username}';")
    if query.next():
        stored = query.value(0)
        return stored == password
    return False
