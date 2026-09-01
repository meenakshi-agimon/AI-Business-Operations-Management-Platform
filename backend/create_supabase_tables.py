import os
import urllib.parse
from pathlib import Path

import psycopg
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / '.env')

user = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')
host = os.getenv('DB_HOST')
port = os.getenv('DB_PORT')
db = os.getenv('DB_NAME')
sql_path = Path(r'Z:\AI-Business-Operations-Management-Platform\database\create_database .sql')
sql = sql_path.read_text(encoding='utf-8')

dsn = f"postgresql://{urllib.parse.quote_plus(user)}:{urllib.parse.quote_plus(password)}@{host}:{port}/{db}?sslmode=require"
conn = psycopg.connect(dsn, connect_timeout=20)
conn.autocommit = True

with conn.cursor() as cur:
    cur.execute(sql)
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_name IN ('employees', 'projects') ORDER BY table_name;")
    print(cur.fetchall())

conn.close()
