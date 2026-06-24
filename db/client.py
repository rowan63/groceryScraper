import os, psycopg2
from dotenv import load_dotenv
load_dotenv()
_conn = None
def get_conn():
    global _conn
    if _conn is None or _conn.closed: _conn = psycopg2.connect(os.environ["DATABASE_URL"])
    return _conn
def close():
    global _conn
    if _conn and not _conn.closed: _conn.close(); _conn = None
