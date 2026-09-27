# NWIS — National Well Intelligence System

> **AI-powered drilling intelligence, risk prediction, historical knowledge retrieval, nearby-well intelligence, real-time monitoring, explainable AI, alerts, and recommendations.**

NWIS is an integrated drilling intelligence platform designed to help drilling engineers understand historical well data, monitor active wells, identify nearby/offset wells, predict drilling risks, explain ML predictions, and receive actionable alerts and recommendations.

---

## 1. What NWIS Does

NWIS combines multiple intelligence modules into one application:

```text
                         ┌──────────────────────┐
                         │      NWIS FRONTEND   │
                         │   React + Vite + UI   │
                         └───────────┬──────────┘
                                     │
                              REST / WebSocket
                                     │
                         ┌───────────▼──────────┐
                         │     FASTAPI BACKEND  │
                         │      API Gateway     │
                         └───────────┬──────────┘
                                     │
       ┌─────────────────────────────┼─────────────────────────────┐
       │                             │                             │
       ▼                             ▼                             ▼
 ┌─────────────┐              ┌─────────────┐              ┌─────────────┐
 │ Historical  │              │ Geo / Wells │              │ Real-Time   │
 │ Knowledge   │              │ Intelligence│              │ eRTMAC      │
 └──────┬──────┘              └──────┬──────┘              └──────┬──────┘
        │                            │                            │
        ▼                            ▼                            ▼
 ┌─────────────┐              ┌─────────────┐              ┌─────────────┐
 │ OCR + NLP   │              │ Nearby Well │              │ Anomaly     │
 │ Extraction  │              │ Analysis    │              │ Detection   │
 └──────┬──────┘              └──────┬──────┘              └──────┬──────┘
        │                            │                            │
        └──────────────┬─────────────┴──────────────┬─────────────┘
                       │                            │
                       ▼                            ▼
                ┌─────────────┐              ┌─────────────┐
                │ RAG / Vector│              │ ML Risk     │
                │ Retrieval   │              │ Prediction  │
                └──────┬──────┘              └──────┬──────┘
                       │                            │
                       │                            ▼
                       │                     ┌─────────────┐
                       │                     │ SHAP        │
                       │                     │ Explainable │
                       │                     │ AI          │
                       │                     └──────┬──────┘
                       │                            │
                       └──────────────┬─────────────┘
                                      ▼
                              ┌──────────────┐
                              │ Alerts &     │
                              │ Recommendations
                              └──────────────┘
```

---

# 2. Main Features

### Historical Intelligence

* Upload/process historical drilling documents
* OCR extraction
* NLP information extraction
* Extract:

  * Well IDs
  * Formation
  * Depth
  * Drilling parameters
  * Mud losses
  * Kicks
  * Stuck pipe
  * Fishing
  * NPT
  * Cementing problems
  * Casing information
  * Pressure observations
  * Recommendations

### RAG Knowledge Engine

Engineers can ask questions such as:

```text
What happened in nearby wells around 2800–3000 m?

Which wells experienced mud loss?

What mitigation was used for similar incidents?

Show previous stuck pipe incidents.

What lessons were learned from similar wells?
```

### Nearby Well Intelligence

* Search nearby wells
* Radius-based search
* Formation filtering
* Reservoir filtering
* Depth overlap
* Trajectory comparison
* Similar offset wells
* GeoJSON output

### ML Risk Prediction

NWIS can predict drilling risks such as:

* Mud loss
* Stuck pipe
* Kick
* Torque spike
* Overpressure
* Cementing issue
* Drilling anomaly
* NPT

### Explainable AI

Every prediction can be accompanied by feature contributions.

Example:

```text
Torque             +0.21
Pressure           +0.17
Mud Flow           +0.13
ROP                -0.08
WOB                +0.06
```

This allows engineers to understand **why** the model produced a prediction.

### Alert Engine

The system converts predictions and real-time anomalies into alerts.

Example:

```text
HIGH RISK

Potential stuck-pipe condition detected.

Confidence: 87%

Major contributing factors:
- Torque increase
- Reduced ROP
- Pressure deviation
```

### Recommendation Engine

NWIS can generate operational recommendations using:

```text
Current condition
       +
Historical incidents
       +
Nearby wells
       +
ML prediction
       +
SHAP explanation
       ↓
Recommended action
```

### Real-Time Monitoring

NWIS includes an eRTMAC adapter architecture:

```text
eRTMAC
   ↓
Adapter
   ↓
Validation
   ↓
Normalization
   ↓
Real-Time Event
   ↓
Anomaly Detection
   ↓
Risk Prediction
   ↓
Alert
   ↓
Dashboard
```

A mock eRTMAC adapter is included for development.

---

# 3. Project Structure

```text
NWIS/
│
├── backend/
│   ├── app/
│   ├── api/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   └── ...
│
├── frontend/
│   ├── src/
│   ├── components/
│   ├── pages/
│   ├── services/
│   └── ...
│
├── ml/
│   ├── models/
│   ├── training/
│   ├── inference/
│   └── ...
│
├── rag/
│   ├── ingestion/
│   ├── retrieval/
│   ├── vectorstore/
│   └── ...
│
├── ingestion/
│   ├── ocr/
│   ├── nlp/
│   └── ...
│
├── geo/
│   ├── nearby/
│   ├── trajectory/
│   └── ...
│
├── realtime/
│   ├── adapters/
│   ├── events/
│   ├── anomaly/
│   └── websocket/
│
├── tests/
│   ├── integration/
│   ├── backend/
│   ├── ml/
│   ├── geo/
│   └── ...
│
├── contracts/
│   ├── well.schema.json
│   ├── drilling-event.schema.json
│   ├── prediction.schema.json
│   ├── alert.schema.json
│   └── ...
│
├── docs/
│   ├── architecture.md
│   ├── data-contract.md
│   ├── api-contract.md
│   ├── integration-rules.md
│   ├── integration-report.md
│   ├── test-report.md
│   ├── api-compatibility-report.md
│   ├── known-issues.md
│   └── deployment-checklist.md
│
└── README.md
```

---

# 4. Requirements

Install the following before running NWIS.

## Required

### Python

Recommended:

```text
Python 3.11+
```

Check:

```bash
python --version
```

or:

```bash
python3 --version
```

### Node.js

Recommended:

```text
Node.js 18+
```

Check:

```bash
node --version
npm --version
```

### Git

```bash
git --version
```

---

# 5. External Services

NWIS can use the following services.

| Service      | Purpose                  | Required                            |
| ------------ | ------------------------ | ----------------------------------- |
| PostgreSQL   | Main relational database | Yes for full experience             |
| PostGIS      | Geographic queries       | Recommended                         |
| Qdrant       | Vector database / RAG    | Required for full RAG               |
| Ollama / LLM | AI/RAG responses         | Optional depending on configuration |
| eRTMAC       | Real-time drilling data  | No — mock adapter available         |

For development, the mock adapters allow you to experience the system without a production eRTMAC connection.

---

# 6. Clone the Project

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd NWIS
```

If you already downloaded the ZIP:

```bash
unzip NWIS_integrated_QA_fixed.zip
cd NWIS
```

---

# 7. Backend Setup

Open a terminal in the project root.

Create a Python virtual environment:

### Windows

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Upgrade pip:

```bash
python -m pip install --upgrade pip
```

Install backend dependencies.

If the repository contains a requirements file:

```bash
pip install -r backend/requirements.txt
```

If dependencies are defined at the root:

```bash
pip install -r requirements.txt
```

---

# 8. Backend Environment Variables

Create:

```text
backend/.env
```

Example:

```env
APP_ENV=development

HOST=0.0.0.0
PORT=8000

DATABASE_URL=postgresql://postgres:postgres@localhost:5432/nwis

QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION=nwis_documents

MODEL_PATH=ml/models

CORS_ORIGINS=http://localhost:5173

USE_MOCK_ERTMAC=true
```

Use the exact variable names already expected by the corresponding modules if your local `.env.example` differs.

---

# 9. PostgreSQL Setup

Install PostgreSQL.

Create the database:

```sql
CREATE DATABASE nwis;
```

If PostGIS is installed:

```sql
CREATE EXTENSION IF NOT EXISTS postgis;
```

You can verify:

```sql
SELECT PostGIS_Version();
```

Then update:

```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/nwis
```

---

# 10. Qdrant Setup

The easiest development method is Docker.

```bash
docker run -p 6333:6333 qdrant/qdrant
```

Qdrant should now be available at:

```text
http://localhost:6333
```

Verify:

```bash
curl http://localhost:6333
```

On Windows PowerShell:

```powershell
Invoke-WebRequest http://localhost:6333
```

---

# 11. Run Database Initialization

From the project root:

```bash
python -m backend
```

If the project provides a database initialization script, run the corresponding initialization command before starting the API.

For example:

```bash
python scripts/init_db.py
```

or:

```bash
python backend/init_db.py
```

Use the script included in the repository.

---

# 12. Start the Backend API

From the project root:

```bash
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

If the repository's FastAPI entry point is different, use the entry point specified in `backend/`.

Expected:

```text
Uvicorn running on http://127.0.0.1:8000
```

---

# 13. Verify the Backend

Open:

```text
http://localhost:8000/docs
```

This opens the FastAPI Swagger UI.

You should see endpoints for areas such as:

```text
Wells
Documents
Search
Predictions
Alerts
Recommendations
Realtime
```

Also check:

```text
http://localhost:8000/health
```

or the health endpoint exposed by the backend.

---

# 14. Frontend Setup

Open a **new terminal**.

Move into the frontend:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Create:

```text
frontend/.env
```

Example:

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

If the frontend uses a WebSocket URL:

```env
VITE_WS_URL=ws://localhost:8000
```

Use the variable names already present in the frontend's API service if they differ.

---

# 15. Start the Frontend

From:

```text
frontend/
```

run:

```bash
npm run dev
```

You should see something similar to:

```text
Local: http://localhost:5173/
```

Open:

```text
http://localhost:5173
```

This is the main NWIS application.

---

# 16. Recommended Startup Order

For the smoothest experience, start services in this order:

```text
1. PostgreSQL
        ↓
2. Qdrant
        ↓
3. Backend / FastAPI
        ↓
4. Mock eRTMAC
        ↓
5. Frontend
```

In development:

### Terminal 1 — PostgreSQL

Make sure PostgreSQL is running.

### Terminal 2 — Qdrant

```bash
docker run -p 6333:6333 qdrant/qdrant
```

### Terminal 3 — Backend

```bash
.venv\Scripts\activate
uvicorn backend.app.main:app --reload --port 8000
```

### Terminal 4 — Frontend

```bash
cd frontend
npm run dev
```

Then open:

```text
http://localhost:5173
```

---

# 17. Experiencing the Complete NWIS Application

After opening the frontend, follow this workflow.

---

## Step 1 — Overview Dashboard

Start from:

```text
Overview Dashboard
```

The dashboard provides a high-level view of:

* Active wells
* Drilling activity
* Current risks
* Alerts
* Nearby wells
* Recent events
* Model predictions

---

# 18. Step 2 — Explore Nearby Wells

Open:

```text
Nearby Wells
```

Select an active well.

The system can display:

```text
Active Well
      │
      ├── Nearby Wells
      ├── Distance
      ├── Formation
      ├── Reservoir
      ├── Depth Overlap
      └── Trajectory
```

Use the map to identify similar offset wells.

---

# 19. Step 3 — Open Well Details

Select a well.

The Well Details page can show:

```text
Well Information

Well ID
Field
Formation
Reservoir
Current Depth
Trajectory
Historical Events
Drilling Parameters
Risk
Predictions
Alerts
```

This is the main context for the intelligence engine.

---

# 20. Step 4 — Historical Intelligence

Open:

```text
Historical Insights
```

Search historical drilling information.

Example:

```text
What happened in wells around 2800-3000 m?
```

Another example:

```text
Which nearby wells experienced mud loss?
```

Another:

```text
What mitigation was used for stuck pipe?
```

The RAG system retrieves relevant historical drilling information.

---

# 21. Step 5 — RAG Knowledge Explorer

Open:

```text
Document / Knowledge Explorer
```

The intended pipeline is:

```text
PDF / Document
      ↓
OCR
      ↓
Text
      ↓
NLP Extraction
      ↓
Structured Knowledge
      ↓
Chunking
      ↓
Embeddings
      ↓
Qdrant
      ↓
Retriever
      ↓
RAG
```

This converts historical documents into searchable drilling knowledge.

---

# 22. Step 6 — Risk Dashboard

Open:

```text
Risk Dashboard
```

You can inspect predicted drilling risks.

Example:

```text
Risk
-----------------------
Stuck Pipe       HIGH
Mud Loss         MEDIUM
Kick             LOW
Overpressure     MEDIUM
Torque Spike     HIGH
```

The actual values depend on the available dataset/model.

---

# 23. Step 7 — ML Prediction

Select a well and provide/currently retrieve drilling parameters such as:

```text
Depth
ROP
WOB
RPM
Torque
Pressure
Mud Flow
Mud Weight
```

The ML engine produces a prediction.

Conceptually:

```text
Drilling Parameters
        ↓
Feature Processing
        ↓
ML Model
        ↓
Risk Prediction
```

---

# 24. Step 8 — SHAP Explanation

After a prediction, open:

```text
Prediction Explanation
```

The system explains which parameters influenced the prediction.

Example:

```text
Prediction: HIGH RISK

Feature              Contribution

Torque                 +0.21
Pressure               +0.17
Mud Weight             +0.14
WOB                    +0.10
ROP                    -0.08
RPM                    -0.04
```

This makes the prediction more understandable to drilling engineers.

---

# 25. Step 9 — Alerts

Open:

```text
Alerts & Recommendations
```

The alert engine combines:

```text
ML Prediction
     +
SHAP Explanation
     +
Real-Time Anomaly
     +
Historical Knowledge
     +
Nearby Well Evidence
```

and produces an operational alert.

Example:

```text
HIGH PRIORITY ALERT

Possible Stuck Pipe Risk

Observed:
- Increasing torque
- Reduced ROP
- Pressure deviation

Historical evidence:
Similar conditions were observed
in offset wells.

Recommended investigation:
Check drilling parameters and
stuck-pipe indicators.
```

---

# 26. Step 10 — Recommendations

The recommendation engine uses:

```text
Current drilling state
        +
Risk prediction
        +
SHAP features
        +
Historical incidents
        +
Nearby wells
        +
RAG knowledge
        ↓
Recommendation
```

The recommendation should be treated as **decision support**, not an autonomous drilling command.

---

# 27. Step 11 — Real-Time Monitoring

Open:

```text
Active Well Monitoring
```

The development system can use:

```text
MockERTMACAdapter
```

instead of a real eRTMAC connection.

The flow is:

```text
Mock eRTMAC
     ↓
Real-Time Adapter
     ↓
Validation
     ↓
Normalization
     ↓
Real-Time Event
     ↓
Anomaly Detection
     ↓
Risk Prediction
     ↓
Alert
     ↓
WebSocket
     ↓
Dashboard
```

This allows the frontend to demonstrate the real-time workflow without requiring access to production eRTMAC infrastructure.

---

# 28. Running the Mock Real-Time System

Set:

```env
USE_MOCK_ERTMAC=true
```

Start the backend.

The realtime service should generate simulated drilling events.

Monitor the browser's:

```text
Active Well Monitoring
```

page.

You should see changing values such as:

```text
Depth
ROP
WOB
RPM
Torque
Pressure
Mud Flow
```

When an abnormal condition is generated:

```text
Normal
  ↓
Anomaly
  ↓
Risk
  ↓
Alert
```

the dashboard should reflect the event.

---

# 29. WebSocket Testing

The frontend connects to the backend realtime channel.

Typical architecture:

```text
Backend
   │
   │ WebSocket
   ▼
React Dashboard
```

When a new event arrives:

```text
Real-Time Event
      ↓
Frontend State
      ↓
Charts
      ↓
Risk Indicator
      ↓
Alert Panel
```

Use the browser developer console to verify WebSocket activity if necessary.

---

# 30. Full Demo Scenario

For a complete demonstration, use this sequence.

### Phase 1 — Historical Knowledge

```text
Open Historical Insights
        ↓
Search historical incidents
        ↓
Retrieve similar wells/events
```

### Phase 2 — Nearby Well Intelligence

```text
Open Nearby Wells
        ↓
Select active well
        ↓
Search nearby wells
        ↓
Compare formation/depth/trajectory
```

### Phase 3 — Prediction

```text
Open Risk Dashboard
        ↓
Select well
        ↓
Run prediction
        ↓
View risk
```

### Phase 4 — Explainability

```text
Open prediction explanation
        ↓
View SHAP contributions
```

### Phase 5 — Decision Support

```text
Open Alerts
        ↓
View alert
        ↓
View supporting evidence
        ↓
View recommendation
```

### Phase 6 — Real-Time

```text
Open Active Well Monitoring
        ↓
Start mock eRTMAC
        ↓
Observe live parameters
        ↓
Anomaly occurs
        ↓
Risk prediction
        ↓
Alert
        ↓
Frontend dashboard update
```

This demonstrates the complete NWIS concept.

---

# 31. Running Tests

Activate the Python environment:

```bash
.venv\Scripts\activate
```

Run the complete Python test suite:

```bash
pytest -q
```

Run integration tests:

```bash
pytest tests/integration -v
```

Run backend tests:

```bash
pytest tests/backend -v
```

Run ML tests:

```bash
pytest tests/ml -v
```

Run geo tests:

```bash
pytest tests/geo -v
```

Run realtime tests:

```bash
pytest tests/realtime -v
```

---

# 32. Integration Test Pipeline

The main integration test validates:

```text
Historical Documents
        ↓
OCR
        ↓
NLP Extraction
        ↓
Database Contract
        ↓
Vector Database
        ↓
RAG Retrieval
        ↓
Nearby Wells
        ↓
ML Prediction
        ↓
SHAP
        ↓
Alert
        ↓
Recommendation
        ↓
Frontend Contract
```

Realtime integration validates:

```text
eRTMAC
   ↓
Anomaly Detection
   ↓
Risk Prediction
   ↓
Alert
   ↓
Dashboard
```

---

# 33. API Documentation

Once the backend is running, open:

```text
http://localhost:8000/docs
```

FastAPI provides an interactive Swagger interface.

You can test APIs directly from the browser.

The major API groups include:

```text
/api/v1/wells
/api/v1/documents
/api/v1/search
/api/v1/predictions
/api/v1/alerts
/api/v1/recommendations
```

Check the generated Swagger documentation for the exact available routes.

---

# 34. Frontend ↔ Backend Configuration

The frontend should point to the running backend.

Example:

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

Therefore:

```text
React
  ↓
http://localhost:8000/api/v1
  ↓
FastAPI
```

Do **not** use:

```text
http://localhost:5173/api/v1
```

unless a frontend proxy has explicitly been configured.

---

# 35. Production Deployment

The application can be deployed as separate services.

Recommended architecture:

```text
                    Internet
                       │
                       ▼
                ┌──────────────┐
                │   Vercel     │
                │   Frontend   │
                └──────┬───────┘
                       │
                       │ HTTPS
                       ▼
                ┌──────────────┐
                │   Backend    │
                │   FastAPI    │
                └──────┬───────┘
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
     PostgreSQL      Qdrant      ML/RAG
          │                         │
          └────────────┬────────────┘
                       │
                       ▼
                  Intelligence
                    Engine
```

The frontend environment should point to the deployed backend:

```env
VITE_API_BASE_URL=https://YOUR-BACKEND-DOMAIN/api/v1
```

For WebSockets:

```env
VITE_WS_URL=wss://YOUR-BACKEND-DOMAIN
```

Use `wss://` when the production site uses HTTPS.

---

# 36. Production Checklist

Before deployment verify:

```text
[ ] PostgreSQL running
[ ] PostGIS enabled
[ ] Qdrant available
[ ] Backend environment variables configured
[ ] Frontend environment variables configured
[ ] CORS configured
[ ] ML model files available
[ ] RAG/vector collection initialized
[ ] Database migrations/schema applied
[ ] WebSocket endpoint accessible
[ ] Mock eRTMAC disabled/replaced for production
[ ] Real eRTMAC credentials configured
[ ] OCR dependencies installed
[ ] API health endpoint working
[ ] Frontend production build succeeds
[ ] Integration tests pass
```

---

# 37. Troubleshooting

## Backend does not start

Check Python:

```bash
python --version
```

Activate the virtual environment:

```powershell
.venv\Scripts\activate
```

Then reinstall dependencies:

```bash
pip install -r backend/requirements.txt
```

---

## Frontend does not start

Run:

```bash
cd frontend
npm install
npm run dev
```

If Vite reports dependency problems:

```bash
rm -rf node_modules
rm package-lock.json
npm install
```

On Windows PowerShell:

```powershell
Remove-Item -Recurse -Force node_modules
Remove-Item package-lock.json
npm install
```

---

## Frontend cannot connect to backend

Check:

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

Then restart Vite:

```bash
npm run dev
```

Environment variables beginning with `VITE_` are loaded when Vite starts, so changing `.env` requires restarting the development server.

---

## CORS error

Verify the backend allows:

```text
http://localhost:5173
```

Example:

```env
CORS_ORIGINS=http://localhost:5173
```

---

## Database connection error

Verify PostgreSQL is running.

Check:

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/nwis
```

Test the connection using your PostgreSQL client.

---

## Qdrant connection error

Start Qdrant:

```bash
docker run -p 6333:6333 qdrant/qdrant
```

Check:

```text
http://localhost:6333
```

---

## No realtime data

Check:

```env
USE_MOCK_ERTMAC=true
```

Restart the backend.

For production, replace the mock adapter with the real eRTMAC adapter.

---

# 38. Important Development Principle

NWIS uses modular architecture.

Do not directly rewrite one module to accommodate another module.

Instead use:

```text
contracts/
```

as the integration boundary.

The main contract categories are:

```text
Well
Drilling Event
Prediction
SHAP Explanation
Alert
Recommendation
GeoJSON
Realtime Event
```

When changing a module:

```text
Module Change
     ↓
Check Contract
     ↓
Update Tests
     ↓
Run Integration Tests
     ↓
Verify Frontend
```

---

# 39. Integration Documentation

Additional QA documentation is available in:

```text
docs/
```

Important files:

```text
docs/architecture.md
docs/data-contract.md
docs/api-contract.md
docs/integration-rules.md
docs/integration-report.md
docs/test-report.md
docs/api-compatibility-report.md
docs/known-issues.md
docs/deployment-checklist.md
```

These documents describe how the independently developed NWIS modules communicate with one another.

---

# 40. Recommended Demo Presentation

For a project demonstration, use this order:

```text
1. Login / Landing Dashboard
           ↓
2. Overview Dashboard
           ↓
3. Nearby Wells Map
           ↓
4. Well Details
           ↓
5. Historical Knowledge
           ↓
6. RAG Search
           ↓
7. Risk Prediction
           ↓
8. SHAP Explanation
           ↓
9. Alert
           ↓
10. Recommendation
           ↓
11. Real-Time Monitoring
           ↓
12. eRTMAC Simulation
           ↓
13. Live Anomaly
           ↓
14. Risk Update
           ↓
15. Live Alert
```

This gives the clearest demonstration of the complete NWIS intelligence pipeline.

---

# 41. One-Command Development Summary

After initial setup, the normal workflow is:

### Terminal 1

```bash
docker run -p 6333:6333 qdrant/qdrant
```

### Terminal 2

```bash
.venv\Scripts\activate
uvicorn backend.app.main:app --reload --port 8000
```

### Terminal 3

```bash
cd frontend
npm run dev
```

Then open:

```text
http://localhost:5173
```

Backend API:

```text
http://localhost:8000
```

Swagger:

```text
http://localhost:8000/docs
```

---

# 42. Final Architecture

The final integrated NWIS platform is:

```text
                         NWIS
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
        ▼                 ▼                 ▼
   HISTORICAL          REAL-TIME          GEO
   INTELLIGENCE        INTELLIGENCE       INTELLIGENCE
        │                 │                 │
        ▼                 ▼                 ▼
    OCR + NLP          eRTMAC            Nearby Wells
        │                 │                 │
        ▼                 ▼                 │
   Vector DB          Anomaly              │
        │              Detection            │
        ▼                 │                 │
       RAG                └───────┐         │
        │                         │         │
        └──────────────┬──────────┘         │
                       ▼                    │
                 ML RISK ENGINE ◄──────────┘
                       │
                       ▼
                    SHAP
                       │
                       ▼
                    ALERT
                       │
                       ▼
                RECOMMENDATION
                       │
                       ▼
                ┌─────────────┐
                │   FASTAPI   │
                └──────┬──────┘
                       │
                REST + WebSocket
                       │
                       ▼
                ┌─────────────┐
                │   REACT     │
                │  FRONTEND   │
                └─────────────┘
```

---

## NWIS is ready for local integrated demonstration

The recommended first run is:

```bash
# 1. Start Qdrant
docker run -p 6333:6333 qdrant/qdrant

# 2. Start backend
uvicorn backend.app.main:app --reload --port 8000

# 3. Start frontend
cd frontend
npm install
npm run dev
```

Then visit:

```text
http://localhost:5173
```

Use the **Nearby Wells → Historical/RAG → Risk Prediction → SHAP → Alerts → Real-Time Monitoring** flow to experience the complete integrated NWIS system.
