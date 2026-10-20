import pandas as pd
from .db import connect

AIRPORTS = [
 ("DEL","VIDP","Indira Gandhi International","Delhi",28.5562,77.1000),
 ("BOM","VABB","Chhatrapati Shivaji Maharaj International","Mumbai",19.0896,72.8656),
 ("BLR","VOBL","Kempegowda International","Bengaluru",13.1986,77.7066),
 ("MAA","VOMM","Chennai International","Chennai",12.9941,80.1709),
 ("HYD","VOHS","Rajiv Gandhi International","Hyderabad",17.2403,78.4294),
 ("CCU","VECC","Netaji Subhas Chandra Bose International","Kolkata",22.6547,88.4467),
 ("COK","VOCI","Cochin International","Kochi",10.1520,76.4019),
 ("AMD","VAAH","Sardar Vallabhbhai Patel International","Ahmedabad",23.0772,72.6347),
]

def rows(sql, params=()):
    with connect() as con:
        return [dict(r) for r in con.execute(sql, params).fetchall()]

def count_flights():
    return rows('SELECT COUNT(*) n FROM flights')[0]['n']

def get_airports(): return rows('SELECT * FROM airports ORDER BY city')

def get_kpis():
    return rows('''SELECT COUNT(*) total_flights,
      ROUND(100.0*AVG(CASE WHEN is_delayed=0 THEN 1.0 ELSE 0.0 END),1) on_time_pct,
      ROUND(AVG(delay_minutes),1) avg_delay,
      SUM(CASE WHEN is_delayed=1 THEN 1 ELSE 0 END) delayed_flights,
      MIN(flight_date) date_start, MAX(flight_date) date_end FROM flights''')[0]

def airport_performance():
    return rows('''SELECT a.iata_code code,a.city,COUNT(f.flight_id) flights,
      ROUND(AVG(f.delay_minutes),1) avg_delay,
      ROUND(100.0*AVG(CASE WHEN f.is_delayed=0 THEN 1.0 ELSE 0.0 END),1) on_time_pct
      FROM airports a LEFT JOIN flights f ON f.origin=a.iata_code
      GROUP BY a.iata_code ORDER BY avg_delay DESC''')

def temporal():
    return rows('''SELECT substr(scheduled_departure,1,2) hour, COUNT(*) flights,
      ROUND(AVG(delay_minutes),1) avg_delay,
      ROUND(100.0*AVG(CASE WHEN is_delayed=0 THEN 1.0 ELSE 0.0 END),1) on_time_pct
      FROM flights GROUP BY hour ORDER BY hour''')

def routes():
    return rows('''SELECT origin,destination,COUNT(*) flights,ROUND(AVG(delay_minutes),1) avg_delay,
      ROUND(100.0*AVG(CASE WHEN is_delayed=0 THEN 1.0 ELSE 0.0 END),1) on_time_pct,
      ROUND(AVG(distance_km),0) distance_km FROM flights GROUP BY origin,destination
      ORDER BY flights DESC''')

def explorer(page=1,page_size=20,origin=None,destination=None,status=None,search=None):
    clauses=[]; params=[]
    if origin: clauses.append('origin=?'); params.append(origin)
    if destination: clauses.append('destination=?'); params.append(destination)
    if status=='delayed': clauses.append('is_delayed=1')
    if status=='on-time': clauses.append('is_delayed=0')
    if search:
        clauses.append('(flight_number LIKE ? OR airline LIKE ? OR origin LIKE ? OR destination LIKE ?)')
        params += [f'%{search}%']*4
    where=(' WHERE '+' AND '.join(clauses)) if clauses else ''
    with connect() as con:
        total=con.execute('SELECT COUNT(*) FROM flights'+where,params).fetchone()[0]
        data=[dict(r) for r in con.execute('SELECT * FROM flights'+where+' ORDER BY flight_date DESC, scheduled_departure LIMIT ? OFFSET ?',params+[page_size,(page-1)*page_size]).fetchall()]
    return {'items':data,'total':total,'page':page,'page_size':page_size,'pages':max(1,(total+page_size-1)//page_size)}

def monthly():
    return rows('''SELECT substr(flight_date,1,7) month,COUNT(*) flights,ROUND(AVG(delay_minutes),1) avg_delay,
      ROUND(100.0*AVG(CASE WHEN is_delayed=0 THEN 1.0 ELSE 0.0 END),1) on_time_pct
      FROM flights GROUP BY month ORDER BY month''')

def airline_stats():
    return rows('''SELECT airline,COUNT(*) flights,ROUND(AVG(delay_minutes),1) avg_delay,
      ROUND(100.0*AVG(CASE WHEN is_delayed=0 THEN 1.0 ELSE 0.0 END),1) on_time_pct
      FROM flights GROUP BY airline ORDER BY avg_delay''')

def quality():
    with connect() as con:
        log=con.execute('SELECT * FROM import_log ORDER BY id DESC LIMIT 1').fetchone()
        nulls=con.execute('SELECT SUM(CASE WHEN delay_minutes IS NULL THEN 1 ELSE 0 END) FROM flights').fetchone()[0]
    return {'record_count':count_flights(),'null_delay_count':nulls or 0,'latest_import':dict(log) if log else None,
            'data_note':'DEMO DATA: generated records are illustrative, not actual flight operations.' if rows("SELECT COUNT(*) n FROM flights WHERE data_source='synthetic_demo'")[0]['n'] else 'Imported dataset; inspect source and licence in README.'}
