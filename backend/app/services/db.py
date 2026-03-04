
import sqlite3
from ..core.config import DB_PATH

def get_conn():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con

