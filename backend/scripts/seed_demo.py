import sys, math, random
from pathlib import Path
from datetime import date, timedelta
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.db import init_db, connect
from app.data_service import AIRPORTS

random.seed(42)
init_db()
with connect() as con:
    con.executemany('INSERT OR REPLACE INTO airports VALUES (?,?,?,?,?,?)', AIRPORTS)
    count=con.execute('SELECT COUNT(*) FROM flights').fetchone()[0]
    if count:
        print(f'Database already has {count} flights; keeping existing data.'); raise SystemExit(0)
    codes=[a[0] for a in AIRPORTS]
    coords={a[0]:(a[4],a[5]) for a in AIRPORTS}
    airlines=['IndiGo','Air India','Akasa Air','SpiceJet']
    rows=[]
    start=date(2025,1,1)
    for day in range(365):
        d=start+timedelta(days=day)
        for origin in codes:
            destinations=[x for x in codes if x!=origin]
            random.shuffle(destinations)
            for destination in destinations[:random.randint(2,4)]:
                for _ in range(random.randint(1,2)):
                    hour=random.choices(range(6,24),weights=[1,1,1,2,2,2,3,3,3,3,3,3,3,3,2,2,1,1])[0]
                    minute=random.choice([0,10,15,20,25,30,35,40,45,50,55])
                    dep=f'{hour:02d}:{minute:02d}'
                    lat1,lon1=coords[origin]; lat2,lon2=coords[destination]
                    # Haversine distance, km
                    p1,p2=math.radians(lat1),math.radians(lat2)
                    dl=math.radians(lon2-lon1); dp=p2-p1
                    aa=math.sin(dp/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
                    dist=6371*2*math.asin(min(1,math.sqrt(aa)))
                    dur=max(45,round(dist/700*60+35))
                    total=hour*60+minute+dur
                    arr=f'{(total//60)%24:02d}:{total%60:02d}'
                    # explicitly simulated delay patterns, not real operational measurements
                    base=random.gauss(8,14)+(10 if hour>=17 else 0)+(7 if origin in ('DEL','BOM') and hour>=16 else 0)
                    delay=round(max(-5,min(115,base)),1)
                    rows.append((f'{random.choice(["6E","AI","QP","SG"])}{random.randint(100,9999)}',random.choice(airlines),origin,destination,d.isoformat(),dep,arr,dur,round(dist,1),delay,int(delay>15),'synthetic_demo'))
    con.executemany('''INSERT INTO flights(flight_number,airline,origin,destination,flight_date,scheduled_departure,scheduled_arrival,scheduled_duration_min,distance_km,delay_minutes,is_delayed,data_source) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)''',rows)
    print(f'Seeded {len(rows)} clearly labelled synthetic demo records.')
