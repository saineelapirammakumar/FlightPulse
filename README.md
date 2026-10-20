# FlightPulse — Aviation Delay Analytics

A student-friendly full-stack data science project about flight routes and delay patterns across eight Indian airports: DEL, BOM, BLR, MAA, HYD, CCU, COK and AMD.

## What's included

- **Redesigned light UI:** a white left sidebar, responsive layouts, a blue aviation-inspired palette, an illustrated route-network hero, KPI cards, route rankings, airport punctuality indicators, and clear provenance warnings.
- **React + Vite + Recharts** dashboard with Overview, Route Intelligence, Delay Prediction, Advanced Analysis, Route Explorer, hypothetical Delay Propagation, and Data Audit pages. The Overview emphasizes route and airport information rather than a wall of charts.
- **FastAPI** backend with documented endpoints at `http://127.0.0.1:8000/docs`.
- **SQLite** database, airport reference table, flight table and import audit log.
- **Pandas / scikit-learn** data preparation and a simple baseline vs Random Forest classifier.
- CSV import script with schema and value validation.

## UI notes

The Network Overview includes a schematic route-network illustration based on the supported airport codes and the route volume returned by the API; it is not a navigational or geographic map. The Data Audit page summarizes the current data provenance and quality endpoint. CSV ingestion is handled by the backend import script; the current API does not expose a browser-based CSV upload endpoint.

## Important data honesty note

The application seeds a reproducible **synthetic demo dataset** so the software can be run immediately. It is not real flight-operation data. Dashboard metrics and model evaluation results generated from it are only demonstrations of the pipeline and must not be presented as actual Indian aviation statistics or real-world model performance.

For real data, use a CSV you have permission to use and check its licence and provenance. The import script requires these columns:

`flight_number, airline, origin, destination, flight_date, scheduled_departure, scheduled_arrival, scheduled_duration_min, distance_km, delay_minutes`

Optional: `is_delayed`. If absent, the script derives it as `delay_minutes > 15`. Dates must be `YYYY-MM-DD`, times `HH:MM`, airport codes must be among the eight supported airports, and delay minutes must be numeric. **Only import genuine delay labels if the source actually documents them.** Do not add fake delay labels to real schedules.

## Easiest Windows startup

1. Install Python 3.10+ and Node.js 20 LTS if not already installed.
2. Double-click `START_BACKEND.bat` and wait for the API to start. Keep its window open.
3. Double-click `START_FRONTEND.bat` in a second window and wait for Vite to show its local URL.
4. Open `http://127.0.0.1:5173`.

The first run downloads Python and JavaScript packages, so it needs internet access. The frontend dependencies are declared in `frontend/package.json`; `START_FRONTEND.bat` installs them automatically on first launch. If installation fails, check your internet connection and run `npm install` from the `frontend` folder, then retry `npm run dev`.

## Windows setup (PowerShell)

Prerequisites: Python 3.10+ and Node.js 18+ (Node.js 20 LTS recommended). Open the `FlightPulse` folder in VS Code or Antigravity.

### 1. Start the backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python scripts/seed_demo.py
python ml/train.py
uvicorn app.main:app --reload --port 8000
```

Keep this terminal running. If PowerShell blocks virtual-environment activation, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in that terminal and activate again. You can also run `.venv\Scripts\python.exe -m pip install -r requirements.txt` and `.venv\Scripts\python.exe scripts\seed_demo.py` without activating.

### 2. Start the frontend in a second terminal

```powershell
cd frontend
npm install
npm run dev
```

Open the URL Vite prints, normally `http://127.0.0.1:5173`.

### 3. Verify the API

- Health check: `http://127.0.0.1:8000/api/health`
- API docs: `http://127.0.0.1:8000/docs`
- Dataset status: `http://127.0.0.1:8000/api/system/status`

## Importing a real CSV

First back up `backend/data/flightpulse.db`. With the backend stopped, run from `backend`:

```powershell
python scripts/import_data.py "C:\path\to\your_flights.csv"
python ml/train.py
```

This adds validated rows to the existing database. To replace demo data rather than append, stop the backend, back up the database, delete `backend/data/flightpulse.db`, run `python scripts/seed_demo.py` only if you still want demo data, and then import your CSV. To use only real data, initialise the database and airport reference rows without seeding demo rows; the API initialises airport metadata on startup. Then run the import script and train the model.

The CSV importer expects normalized column names listed above; it does not automatically infer arbitrary source column names. Inspect and transform your source data first. Keep source data files out of Git if you do not have permission to redistribute them.

## Model details

- Target: `is_delayed = 1` if the observed `delay_minutes > 15`, otherwise `0` (unless a documented source label is supplied).
- Features: origin, destination, airline, scheduled departure hour, weekday, month, scheduled duration and distance.
- Models: majority-class baseline and Random Forest classifier.
- Split: chronological first 80% for training and final 20% for testing.
- Metrics: accuracy, precision, recall, F1, ROC-AUC and confusion matrix.

This is a simple educational baseline, not an operational airline prediction service. For valid real-world performance claims, use a suitable real dataset, verify feature availability at prediction time, check class balance, and review the test metrics.

## API endpoints

- `GET /api/health`
- `GET /api/system/status`
- `GET /api/airports`
- `GET /api/overview/kpis`
- `GET /api/overview/airports`
- `GET /api/analysis/temporal`
- `GET /api/analysis/airlines`
- `GET /api/routes/corridors`
- `GET /api/explorer/flights?page=1&page_size=15&origin=DEL&status=delayed`
- `GET /api/quality`
- `GET /api/prediction/metrics`
- `POST /api/prediction/predict`
- `GET /api/propagation/demo?initial_delay=45`

## Folder structure

```text
FlightPulse/
  backend/
    app/              FastAPI, SQLite and analytics
    data/             SQLite database is created here
    ml/               training script and model artifacts
    scripts/          demo seeding and CSV import
    requirements.txt
  frontend/
    src/App.jsx       Dashboard views and interactions
    src/styles.css    Responsive styling
    package.json
  README.md
```

## Troubleshooting

- **Frontend says backend disconnected:** confirm the backend terminal is still running on port 8000.
- **Model is not trained:** run `python ml/train.py` from the `backend` directory after seeding/importing data.
- **`npm` not recognized:** install Node.js LTS and reopen the terminal.
- **CSV import rejects rows:** verify required column names, date/time formats, numeric values, and supported airport codes.
