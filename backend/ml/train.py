"""Train a transparent baseline and Random Forest classifier from imported flight records.
For synthetic_demo rows, metrics describe only the simulation, not real-world performance.
"""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pandas as pd
from joblib import dump
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.dummy import DummyClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
from app.db import connect

BASE=Path(__file__).resolve().parents[1]; MODEL_DIR=BASE/'ml'; MODEL_DIR.mkdir(exist_ok=True)
FEATURES=['origin','destination','airline','departure_hour','day_of_week','month','scheduled_duration_min','distance_km']
CAT=['origin','destination','airline']; NUM=[c for c in FEATURES if c not in CAT]
def metrics(model,X,y):
    pred=model.predict(X); result={'accuracy':round(float(accuracy_score(y,pred)),4),'precision':round(float(precision_score(y,pred,zero_division=0)),4),'recall':round(float(recall_score(y,pred,zero_division=0)),4),'f1':round(float(f1_score(y,pred,zero_division=0)),4),'confusion_matrix':confusion_matrix(y,pred,labels=[0,1]).tolist()}
    try: result['roc_auc']=round(float(roc_auc_score(y,model.predict_proba(X)[:,1])),4)
    except Exception: result['roc_auc']=None
    return result
def main():
    with connect() as con: df=pd.read_sql_query('SELECT * FROM flights ORDER BY flight_date,scheduled_departure',con)
    if len(df)<30: raise SystemExit('Need at least 30 valid labelled rows before training.')
    df['departure_hour']=pd.to_numeric(df.scheduled_departure.str.slice(0,2),errors='coerce')
    dt=pd.to_datetime(df.flight_date,errors='coerce'); df['day_of_week']=dt.dt.dayofweek; df['month']=dt.dt.month
    df['is_delayed']=pd.to_numeric(df.is_delayed,errors='coerce'); df=df.dropna(subset=FEATURES+['is_delayed']).sort_values(['flight_date','scheduled_departure'])
    unique_dates=sorted(df.flight_date.unique())
    if len(unique_dates)<2: raise SystemExit('Need at least two distinct flight dates for chronological evaluation.')
    cutoff_index=max(1,min(len(unique_dates)-1,int(len(unique_dates)*.8)))
    cutoff_date=unique_dates[cutoff_index]
    train=df[df.flight_date < cutoff_date]; test=df[df.flight_date >= cutoff_date]
    if train.empty or test.empty: raise SystemExit('Chronological split produced an empty partition; inspect flight dates.')
    if train.is_delayed.nunique()<2: raise SystemExit('Training rows need both delayed and on-time examples; inspect dataset.')
    prep=ColumnTransformer([('cat',OneHotEncoder(handle_unknown='ignore'),CAT),('num','passthrough',NUM)])
    rf=Pipeline([('prep',prep),('model',RandomForestClassifier(n_estimators=120,max_depth=12,min_samples_leaf=2,class_weight='balanced',random_state=42,n_jobs=-1))])
    baseline=DummyClassifier(strategy='most_frequent')
    rf.fit(train[FEATURES],train.is_delayed.astype(int)); baseline.fit(train[FEATURES],train.is_delayed.astype(int))
    dump(rf,MODEL_DIR/'model.joblib'); dump(baseline,MODEL_DIR/'baseline.joblib')
    result={'task':'Predict delay > 15 minutes','target_definition':'is_delayed = delay_minutes > 15 unless supplied in CSV','train_rows':len(train),'test_rows':len(test),'date_train_end':str(train.flight_date.max()),'date_test_start':str(test.flight_date.min()),'data_sources':sorted(df.data_source.unique().tolist()),'baseline':metrics(baseline,test[FEATURES],test.is_delayed.astype(int)),'random_forest':metrics(rf,test[FEATURES],test.is_delayed.astype(int)),'caution':'If data_source includes synthetic_demo, these metrics measure only the generated demo data. They are not evidence of real-world prediction performance.' if 'synthetic_demo' in set(df.data_source) else 'Evaluate results in light of dataset provenance and representativeness.'}
    (MODEL_DIR/'metrics.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))
if __name__=='__main__': main()
