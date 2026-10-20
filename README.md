# FlightPulse — Aviation Delay Analytics

FlightPulse demonstrates how data processing, exploratory data analysis, interactive visualizations, and machine learning can be combined to explore flight delays across the Indian domestic aviation network.

## Project Objective

FlightPulse explores how flight delays can be analysed across a network of eight Indian domestic airports. It combines data processing, exploratory data analysis, interactive visualizations, and a basic machine learning classification pipeline in one full-stack application.

The project demonstrates how route-level and airport-level patterns can be explored, how a delay threshold can define a classification target, and how hypothetical delays may propagate across connecting flight legs.

### Key Objectives

- Analyse flight volume, average delays, and on-time performance.
- Compare routes, airports, and airlines through interactive visualizations.
- Explore temporal patterns in flight delays.
- Demonstrate a machine learning workflow for classifying flights as delayed or not delayed.
- Simulate hypothetical delay propagation through a sequence of connected flights.
- Maintain data-quality checks and clearly document data provenance.

## What's included

- **Redesigned light UI:** a white left sidebar, responsive layouts, a blue aviation-inspired palette, an illustrated route-network hero, KPI cards, route rankings, airport punctuality indicators, and clear provenance warnings.
- **React + Vite + Recharts** dashboard with Overview, Route Intelligence, Delay Prediction, Advanced Analysis, Route Explorer, hypothetical Delay Propagation, and Data Audit pages. The Overview emphasizes route and airport information rather than a wall of charts.
- **FastAPI** backend with documented endpoints at `http://127.0.0.1:8000/docs`.
- **SQLite** database, airport reference table, flight table, and import audit log.
- **Pandas / scikit-learn** data preparation and a simple baseline vs Random Forest classifier.
- CSV import script with schema and value validation.

## Dashboard Preview

Screenshots can help visitors understand the application before running it.

Save screenshots of your actual dashboard in a `screenshots` folder, then uncomment and update the following examples to match the filenames you save.

<!--
![FlightPulse Overview](screenshots/overview.png)

![Route Intelligence](screenshots/route-intelligence.png)

![Delay Prediction](screenshots/delay-prediction.png)

![Advanced Analysis](screenshots/advanced-analysis.png)
-->

## UI Notes

The Network Overview includes a schematic route-network illustration based on the supported airport codes and route volume returned by the API; it is not a navigational or geographic map.

The Data Audit page summarizes the current data provenance and quality endpoint. CSV ingestion is handled by the backend import script; the current API does not expose a browser-based CSV upload endpoint.

## Project Status and Data Limitations

**Current status:** Educational demonstration using synthetic flight records.

The application seeds a reproducible **synthetic demo dataset** so the software can be run immediately. It is not real flight-operation data. Dashboard metrics, predictions, and model evaluation results generated from it are demonstrations of the pipeline and must not be presented as actual Indian aviation statistics or real-world model performance.

The application is designed to support future analysis using a suitable, documented flight dataset. Any real-data results should be reported only after validating the source, licence, date coverage, labels, and data quality.

## Important Data Honesty Note

For real data, use a CSV you have permission to use and check its licence and provenance.

The import script requires these columns:

`flight_number, airline, origin, destination, flight_date, scheduled_departure, scheduled_arrival, scheduled_duration_min, distance_km, delay_minutes`

Optional: `is_delayed`. If absent, the script derives it as `delay_minutes > 15`.

Dates must be `YYYY-MM-DD`, times `HH:MM`, airport codes must be among the eight supported airports, and delay minutes must be numeric.

**Only import genuine delay labels if the source actually documents them.** Do not add fake delay labels to real schedules.

## Easiest Windows Startup

1. Install Python 3.10+ and Node.js 20 LTS if not already installed.
2. Double-click `START_BACKEND.bat` and wait for the API to start. Keep its window open.
3. Double-click `START_FRONTEND.bat` in a second window and wait for Vite to show its local URL.
4. Open `http://127.0.0.1:5173`.

The first run downloads Python and JavaScript packages, so it needs internet access. The frontend dependencies are declared in `frontend/package.json`; `START_FRONTEND.bat` installs them automatically on first launch.

If installation fails, check your internet connection and run `npm install` from the `frontend` folder, then retry `npm run dev`.

## Windows Setup (PowerShell)

Prerequisites: Python 3.10+ and Node.js 18+ (Node.js 20 LTS recommended). Open the `FlightPulse` folder in VS Code or Antigravity.

### 1. Start the Backend

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

Keep this terminal running.

If PowerShell blocks virtual-environment activation, run the following command in that terminal and activate again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

You can also run the following commands without activating the environment:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe scripts\seed_demo.py
```

### 2. Start the Frontend in a Second Terminal

```powershell
cd frontend
npm install
npm run dev
```

Open the URL Vite prints, normally `http://127.0.0.1:5173`.

### 3. Verify the API

- Health check: `http://127.0.0.1:8000/api/health`
- API documentation: `http://127.0.0.1:8000/docs`
- Dataset status: `http://127.0.0.1:8000/api/system/status`

## Importing a Real CSV

First, back up `backend/data/flightpulse.db`. With the backend stopped, run from the `backend` directory:

```powershell
python scripts/import_data.py "C:\path\to\your_flights.csv"
python ml/train.py
```

This adds validated rows to the existing database.

To replace demo data rather than append, stop the backend, back up the database, delete `backend/data/flightpulse.db`, run `python scripts/seed_demo.py` only if you still want demo data, and then import your CSV.

To use only real data, initialise the database and airport reference rows without seeding demo rows; the API initialises airport metadata on startup. Then run the import script and train the model.

The CSV importer expects normalized column names listed above; it does not automatically infer arbitrary source column names. Inspect and transform your source data first.

Keep source data files out of Git if you do not have permission to redistribute them.

## Model Details

- **Target:** `is_delayed = 1` if the observed `delay_minutes > 15`, otherwise `0` (unless a documented source label is supplied).
- **Features:** origin, destination, airline, scheduled departure hour, weekday, month, scheduled duration, and distance.
- **Models:** majority-class baseline and Random Forest classifier.
- **Split:** chronological first 80% for training and final 20% for testing.
- **Metrics:** accuracy, precision, recall, F1, ROC-AUC, and confusion matrix.

This is a simple educational baseline, not an operational airline prediction service.

For valid real-world performance claims, use a suitable real dataset, verify feature availability at prediction time, check class balance, and review the test metrics.

## API Endpoints

The following endpoints are documented for the application. Verify their exact paths against `backend/app/main.py` if the implementation changes.

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

**Important:** The frontend and backend must use matching endpoint paths. For example, if the backend defines `/api/system/airports`, the frontend must request that path rather than `/api/airports`. Check the live API documentation at `http://127.0.0.1:8000/docs` for the routes currently registered by the backend.

## Testing

Run backend tests from the `backend` directory:

```powershell
pytest -q
```

Run a frontend production build from the `frontend` directory:

```powershell
npm run build
```

A successful test run and production build help verify the project setup, but they do not independently establish the accuracy of the analysis or model.

These commands require the relevant test tools and project dependencies to be installed. If no tests are present, add them before relying on the test command as a project verification step.

## Folder Structure

```text
FlightPulse/
  backend/
    app/              FastAPI, SQLite and analytics
    data/             SQLite database is created here
    ml/               Training script and model artifacts
    scripts/          Demo seeding and CSV import
    requirements.txt
  frontend/
    src/
      App.jsx         Dashboard views and interactions
      styles.css      Responsive styling
    package.json
  screenshots/        Optional dashboard screenshots
  README.md
  .gitignore
```

## GitHub and `.gitignore`

Add a `.gitignore` file in the project root so generated files and local environments are not accidentally committed.

At minimum, consider excluding:

```gitignore
# Python
__pycache__/
*.py[cod]
.venv/
venv/
.pytest_cache/

# Node
node_modules/
dist/

# Environment variables and secrets
.env
.env.*

# Local database and generated model files
backend/data/*.db
backend/ml/saved_model.joblib

# Editor and operating-system files
.vscode/
.DS_Store
Thumbs.db
```

**Before committing:** Check whether the database or model artifacts are required for the project demonstration. If you intentionally want to include a small, reproducible demo database or model, adjust the relevant `.gitignore` rules and ensure that no private or restricted data is included.


## Conclusion

FlightPulse is an educational full-stack data science project that brings together data ingestion, SQLite storage, data-quality checks, exploratory analysis, interactive dashboards, and machine learning.

Its primary goal is to demonstrate a complete analytical workflow. Meaningful aviation conclusions and real-world model-performance claims require suitable real flight data, documented provenance, and appropriate validation.
