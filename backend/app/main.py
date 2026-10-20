from pathlib import Path
import sys, json, math
from datetime import datetime
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from .db import init_db, connect
from . import data_service as ds

ROOT=Path(__file__).resolve().parents[1]
app=FastAPI(title='FlightPulse API',version='1.0.0',description='Flight delay analytics and student ML demonstration. Demo data is explicitly labelled.')
app.add_middleware(CORSMiddleware,allow_origins=['http://localhost:5173','http://127.0.0.1:5173'],allow_credentials=True,allow_methods=['*'],allow_headers=['*'])
@app.on_event('startup')
def startup():
    init_db()
    with connect() as con:
        if con.execute('SELECT COUNT(*) FROM airports').fetchone()[0]==0:
            con.executemany('INSERT OR REPLACE INTO airports VALUES (?,?,?,?,?,?)',ds.AIRPORTS)
class PredictInput(BaseModel):
    origin:str; destination:str; airline:str='IndiGo'; scheduled_departure:str=Field(pattern=r'^([01]\d|2[0-3]):[0-5]\d$'); flight_date:str=Field(pattern=r'^\d{4}-\d{2}-\d{2}$'); scheduled_duration_min:int=Field(default=120,ge=20,le=900); distance_km:float=Field(default=800,gt=0,le=6000)
@app.get('/api/health')
def health(): return {'status':'ok','service':'FlightPulse API'}
@app.get('/api/system/status')
def status(): return {'status':'ok','flights':ds.count_flights(),'airports':len(ds.get_airports()),'database':'SQLite','quality':ds.quality()}
@app.get('/api/airports')
def airports(): return ds.get_airports()
@app.get('/api/overview/kpis')
def kpis(): return ds.get_kpis()
@app.get('/api/overview/airports')
def airport_performance(): return ds.airport_performance()
@app.get('/api/analysis/temporal')
def temporal(): return {'hourly':ds.temporal(),'monthly':ds.monthly()}
@app.get('/api/analysis/airlines')
def airlines(): return ds.airline_stats()
@app.get('/api/routes/corridors')
def routes(): return ds.routes()
@app.get('/api/explorer/flights')
def explorer(page:int=Query(1,ge=1),page_size:int=Query(20,ge=1,le=100),origin:str|None=None,destination:str|None=None,status:str|None=None,search:str|None=None):
    return ds.explorer(page,page_size,origin,destination,status,search)
@app.get('/api/quality')
def quality(): return ds.quality()
@app.get('/api/prediction/metrics')
def prediction_metrics():
    p=ROOT/'ml'/'metrics.json'
    if not p.exists(): return {'trained':False,'message':'Train model using: python ml/train.py'}
    return {'trained':True,**json.loads(p.read_text())}
@app.post('/api/prediction/predict')
def predict(payload:PredictInput):
    if payload.origin==payload.destination: raise HTTPException(400,'Origin and destination must be different.')
    codes={a['iata_code'] for a in ds.get_airports()}
    if payload.origin not in codes or payload.destination not in codes: raise HTTPException(400,'Choose one of the eight supported airports.')
    model_path=ROOT/'ml'/'model.joblib'
    if not model_path.exists(): raise HTTPException(503,'Model is not trained yet. Run python ml/train.py in the backend folder.')
    import pandas as pd
    from joblib import load
    d=datetime.strptime(payload.flight_date,'%Y-%m-%d')
    X=pd.DataFrame([{'origin':payload.origin,'destination':payload.destination,'airline':payload.airline,'departure_hour':int(payload.scheduled_departure[:2]),'day_of_week':d.weekday(),'month':d.month,'scheduled_duration_min':payload.scheduled_duration_min,'distance_km':payload.distance_km}])
    model=load(model_path); probability=float(model.predict_proba(X)[0][1]); delayed=probability>=0.5
    return {'prediction':'Delayed (>15 min)' if delayed else 'Likely on-time (≤15 min)','delay_probability':round(probability,4),'risk_level':'High' if probability>=.7 else 'Moderate' if probability>=.4 else 'Lower','note':'This is a model estimate, not a guarantee. Check model evaluation and dataset provenance.'}
@app.get('/api/propagation/demo')
def propagation(initial_delay:int=Query(45,ge=0,le=180)):
    legs=[{'leg':1,'route':'DEL → BOM','buffer':0},{'leg':2,'route':'BOM → BLR','buffer':45},{'leg':3,'route':'BLR → HYD','buffer':50}]
    residual=initial_delay; out=[]
    for leg in legs:
        if leg['leg']>1: residual=max(0,residual-leg['buffer'])
        out.append({**leg,'incoming_delay_min':initial_delay if leg['leg']==1 else out[-1]['residual_delay_min'],'residual_delay_min':residual})
    return {'illustrative_only':True,'initial_delay_min':initial_delay,'legs':out,'note':'Hypothetical arithmetic demonstration, not observed aircraft rotations or proof of causal propagation.'}
