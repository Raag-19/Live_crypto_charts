import sqlite3
import pandas as pd

DB_FILE = 'charts.db'

def get_db_connection(db_file=DB_FILE):
    return sqlite3.connect(db_file)

def init_db(db_file=DB_FILE):
    conn = get_db_connection(db_file)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS candles (
            timestamp INTEGER PRIMARY KEY,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            volume REAL
        )
    ''')
    conn.commit()
    conn.close()

def replace_candles(df, db_file=DB_FILE):
    conn = get_db_connection(db_file)
    df.to_sql('candles', conn, if_exists='replace', index=False, index_label='timestamp')
    conn.close()

def get_candles(db_file=DB_FILE):
    conn = get_db_connection(db_file)
    df = pd.read_sql_query("SELECT * FROM candles ORDER BY timestamp", conn)
    if not df.empty:
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
        df.set_index('timestamp', inplace=True)
    conn.close()
    return df
