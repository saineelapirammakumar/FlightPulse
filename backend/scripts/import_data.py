"""Import a CSV containing flight_number, airline, origin, destination, flight_date,
scheduled_departure, scheduled_arrival, scheduled_duration_min, distance_km, delay_minutes.
Run: python scripts/import_data.py path\to\flights.csv
Optional columns: is_delayed. Existing database rows are retained.
"""
import sys, csv
from pathlib import Path
from datetime import datetime
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.db import init_db, connect
from app.data_service import AIRPORTS

REQUIRED={'flight_number','airline','origin','destination','flight_date','scheduled_departure','scheduled_arrival','scheduled_duration_min','distance_km','delay_minutes'}
def main():
    if len(sys.argv)<2:
        print('Usage: python scripts/import_data.py path/to/flights.csv'); raise SystemExit(2)
    path=Path(sys.argv[1]).expanduser()
    if not path.is_file(): raise SystemExit(f'File not found: {path}')
    init_db(); valid=[]; rejected=0; total=0
    with path.open('r',encoding='utf-8-sig',newline='') as f:
        reader=csv.DictReader(f)
        cols={c.strip() for c in (reader.fieldnames or [])}
        missing=REQUIRED-cols
        if missing: raise SystemExit('Missing required columns: '+', '.join(sorted(missing)))
        for row in reader:
            total+=1
            try:
                origin=row['origin'].strip().upper(); dest=row['destination'].strip().upper()
                if origin not in {a[0] for a in AIRPORTS} or dest not in {a[0] for a in AIRPORTS} or origin==dest: raise ValueError('airport')
                datetime.strptime(row['flight_date'].strip(),'%Y-%m-%d')
                datetime.strptime(row['scheduled_departure'].strip(),'%H:%M')
                datetime.strptime(row['scheduled_arrival'].strip(),'%H:%M')
                delay=float(row['delay_minutes']); duration=int(float(row['scheduled_duration_min'])); distance=float(row['distance_km'])
                if duration<=0 or distance<=0: raise ValueError('duration/distance')
                label=int(float(row.get('is_delayed', int(delay>15))))
                valid.append((row['flight_number'].strip(),row['airline'].strip(),origin,dest,row['flight_date'].strip(),row['scheduled_departure'].strip(),row['scheduled_arrival'].strip(),duration,distance,delay,label,'user_csv:'+path.name))
            except Exception: rejected+=1
    with connect() as con:
        con.executemany('INSERT OR REPLACE INTO airports VALUES (?,?,?,?,?,?)',AIRPORTS)
        con.executemany('''INSERT INTO flights(flight_number,airline,origin,destination,flight_date,scheduled_departure,scheduled_arrival,scheduled_duration_min,distance_km,delay_minutes,is_delayed,data_source) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)''',valid)
        con.execute('INSERT INTO import_log(imported_at,filename,total_rows,imported_rows,rejected_rows,notes) VALUES (?,?,?,?,?,?)',(datetime.now().isoformat(timespec='seconds'),path.name,total,len(valid),rejected,'Rows failing required-field, airport, date, time, or numeric validation were rejected.'))
    print(f'Import complete. Total rows: {total}; imported: {len(valid)}; rejected: {rejected}.')
if __name__=='__main__': main()
