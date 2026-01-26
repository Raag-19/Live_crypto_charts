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

def save_candle(candle_data, db_file=DB_FILE):
    """Saves a single candle to the database."""
    conn = get_db_connection(db_file)
    c = conn.cursor()
    # The websocket gives timestamp in milliseconds, the DB expects seconds
    timestamp_s = candle_data['candle_start_time'] // 1000
    c.execute('''
        INSERT OR REPLACE INTO candles (timestamp, open, high, low, close, volume)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        timestamp_s,
        candle_data['open'],
        candle_data['high'],
        candle_data['low'],
        candle_data['close'],
        candle_data.get('volume', 0)
    ))
    conn.commit()
    conn.close()
