from pathlib import Path
import sqlite3

BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = BASE_DIR / "data" / "flightpulse.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    with connect() as con:
        con.executescript('''
        CREATE TABLE IF NOT EXISTS airports(
          iata_code TEXT PRIMARY KEY, icao_code TEXT NOT NULL, name TEXT NOT NULL,
          city TEXT NOT NULL, latitude REAL NOT NULL, longitude REAL NOT NULL
        );
        CREATE TABLE IF NOT EXISTS flights(
          flight_id INTEGER PRIMARY KEY AUTOINCREMENT,
          flight_number TEXT NOT NULL, airline TEXT NOT NULL,
          origin TEXT NOT NULL REFERENCES airports(iata_code),
          destination TEXT NOT NULL REFERENCES airports(iata_code),
          flight_date TEXT NOT NULL, scheduled_departure TEXT NOT NULL,
          scheduled_arrival TEXT NOT NULL, scheduled_duration_min INTEGER NOT NULL,
          distance_km REAL NOT NULL, delay_minutes REAL, is_delayed INTEGER,
          data_source TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_flights_date ON flights(flight_date);
        CREATE INDEX IF NOT EXISTS idx_flights_route ON flights(origin,destination);
        CREATE TABLE IF NOT EXISTS import_log(
          id INTEGER PRIMARY KEY AUTOINCREMENT, imported_at TEXT NOT NULL,
          filename TEXT NOT NULL, total_rows INTEGER NOT NULL, imported_rows INTEGER NOT NULL,
          rejected_rows INTEGER NOT NULL, notes TEXT NOT NULL
        );
        ''')
