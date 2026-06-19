
from typing import Optional
import os
from PyQt5.QtSql import QSqlDatabase, QSqlQuery

_db = None


def init_db(db_path: Optional[str] = None) -> QSqlDatabase:

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
    query.exec_("create table if not exists user (id integer PRIMARY KEY, user_name string, password string);")
    # ensure default admin exists (ignore errors if duplicate)
    query.exec_("insert or ignore into user (id, user_name, password) values (0, 'admin', '123');")
    return _db


def check_user(username: str, password: str) -> bool:

    if _db is None:
        init_db()
    query = QSqlQuery()
    query.exec_(f"select * from user where user_name='{username}';")
    if query.next():
        stored = str(query.value(2))
        return stored == password
    return False
