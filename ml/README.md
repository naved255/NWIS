# NWIS Drilling Risk Prediction Engine (M10)

Self-contained ML module for predicting one drilling risk at a time from historical/current drilling observations. It is designed to integrate into the larger NWIS repository without coupling to unfinished database, RAG, realtime, SHAP, or frontend implementations.

## Supported risk types

The engine can train separate binary models for:

- `mud_loss`
- `stuck_pipe`
- `kick`
- `torque_spike`
- `overpressure`
- `cementing_issue`
- `npt`
- `drilling_anomaly`

`risk_type=none` is treated as the negative class. The training target may contain any other negative/non-target label; the requested `risk_type` becomes positive.

## Architecture

```text
Raw CSV/DataFrame
      |
      v
Validation + target checks
      |
      v
Point-in-time feature engineering
      |
      v
Chronological train / validation / test split
      |
      +--> train-only imputation/encoding/scaling
      |
      +--> LightGBM / XGBoost / HistGradientBoosting
      |       + class imbalance weighting
      |
      v
Validation threshold tuning
      |
      v
Test evaluation
  precision / recall / F1
  ROC-AUC / PR-AUC / confusion matrix
      |
      v
joblib artifact
(preprocessor + model together)
      |
      v
predict_risk(features)
```

### Leakage controls

1. If a valid timestamp column is supplied, data is sorted chronologically.
2. The latest data is held out as test data and the preceding block as validation data.
3. The preprocessing transformer is fitted only on the training partition.
4. Threshold selection uses validation data only and is never tuned on test data.
5. Feature engineering does not calculate target-derived rolling statistics.
6. Historical/nearby-well aggregates must be supplied as point-in-time values generated upstream; this module does not assume future knowledge.
7. Random splitting is used only when no usable timestamp exists and is explicitly a fallback.

### Imbalance handling

The default approach is class weighting through `scale_pos_weight` for LightGBM/XGBoost (and balanced weighting for the sklearn option). Threshold tuning is performed on validation data. Random oversampling is deliberately not enabled by default because naive oversampling of sequential drilling records can duplicate temporal information and make leakage easier. If a future dataset requires resampling, it should be performed inside the training partition only and ideally with a time-aware strategy.

## Folder structure

```text
ml/risk_engine/
├── risk_engine/
│   ├── __init__.py
│   ├── __main__.py
│   ├── api.py
│   ├── cli.py
│   ├── engine.py
│   ├── features.py
│   ├── metrics.py
│   ├── models.py
│   ├── preprocessing.py
│   ├── schemas.py
│   └── splitting.py
├── tests/
│   ├── test_engine.py
│   ├── test_metrics.py
│   └── test_splitting.py
├── examples/
│   └── sample_training_data.csv
├── train.py
├── requirements.txt
├── pyproject.toml
├── .env.example
└── README.md
```

## Installation

From this directory:

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
# Linux/macOS
# source .venv/bin/activate

pip install -r requirements.txt
pip install -e .
```

Run tests:

```bash
pytest -q
```

## Training

Train a LightGBM model for torque spikes:

```bash
python -m risk_engine train \
  --csv examples/sample_training_data.csv \
  --risk-type torque_spike \
  --model lightgbm \
  --artifact-dir artifacts/torque_spike
```

PowerShell uses the same command but can put it on one line if preferred:

```powershell
python -m risk_engine train --csv examples/sample_training_data.csv --risk-type torque_spike --model lightgbm --artifact-dir artifacts/torque_spike
```

Train using XGBoost:

```bash
python -m risk_engine train --csv path/to/train.csv --risk-type stuck_pipe --model xgboost --artifact-dir artifacts/stuck_pipe
```

Train using only scikit-learn:

```bash
python -m risk_engine train --csv path/to/train.csv --risk-type kick --model hist_gradient_boosting --artifact-dir artifacts/kick
```

The artifact contains:

```text
artifacts/<risk>/
├── model.joblib
└── metadata.json
```

`model.joblib` contains the complete preprocessing + model pipeline, so inference does not require manually reconstructing transformations.

## Python API

```python
import pandas as pd
from risk_engine import RiskPredictionEngine, TrainingConfig

engine = RiskPredictionEngine("artifacts/torque_spike", model_version="1.0.0")
config = TrainingConfig(model_type="lightgbm")
metrics = engine.fit(df, risk_type="torque_spike", config=config)

prediction = engine.predict_risk({
    "depth": 2940,
    "rop": 5.0,
    "wob": 25,
    "rpm": 90,
    "torque": 78,
    "pressure": 350,
    "mud_flow": 200,
    "mud_weight": 10.5,
    "formation": "F3",
    "inclination": 15.0,
    "azimuth": 200,
    "dogleg_severity": 1.8,
    "nearby_well_count": 4,
    "nearby_event_rate": 0.20,
    "historical_risk_rate": 0.18,
})
print(prediction.model_dump())
```

Example response shape:

```json
{
  "risk_type": "torque_spike",
  "probability": 0.81,
  "severity": "high",
  "confidence": 0.89,
  "model_version": "1.0.0"
}
```

`confidence` is intentionally described as **decision-boundary confidence**, not a calibrated probability of correctness. Probability calibration can be added later if validated against sufficient OIL data.

## FastAPI integration

The package exposes a lightweight adapter:

```python
from risk_engine.api import create_app
app = create_app("artifacts/torque_spike")
```

Run:

```bash
uvicorn your_entrypoint:app --host 0.0.0.0 --port 8001
```

### `GET /health`

```json
{
  "status": "ok",
  "model_version": "1.0.0",
  "risk_type": "torque_spike"
}
```

### `POST /predict`

Request:

```json
{
  "features": {
    "depth": 2940,
    "rop": 5,
    "wob": 25,
    "rpm": 90,
    "torque": 78,
    "pressure": 350,
    "mud_flow": 200,
    "mud_weight": 10.5,
    "formation": "F3"
  }
}
```

Response:

```json
{
  "risk_type": "torque_spike",
  "probability": 0.81,
  "severity": "high",
  "confidence": 0.89,
  "model_version": "1.0.0"
}
```

## Integration with the rest of NWIS

### Upstream modules

The risk engine accepts a flat pandas DataFrame/dictionary. Therefore it does not depend on PostgreSQL, PostGIS, Qdrant, document processing, or eRTMAC internals.

Upstream modules should map their data into fields such as:

- `depth`
- `rop`
- `wob`
- `rpm`
- `torque`
- `pressure`
- `mud_flow`
- `mud_weight`
- `formation`
- `inclination`
- `azimuth`
- `dogleg_severity`
- `nearby_well_count`
- `nearby_event_rate`
- `historical_risk_rate`
- `timestamp`
- `well_id`
- `risk_type` for training only

The upstream data layer remains responsible for producing valid point-in-time nearby-well and historical statistics.

### Downstream modules

The output is deliberately small and stable:

```json
{
  "risk_type": "...",
  "probability": 0.0,
  "severity": "low|medium|high|critical",
  "confidence": 0.0,
  "model_version": "..."
}
```

M11/SHAP can independently consume the same feature dictionary plus the persisted model artifact. Alerts/recommendations can consume the prediction JSON without knowing how the model works.

## Important production note

The included CSV is synthetic and exists only for software testing. It is **not OIL data** and must not be presented as historical drilling evidence. Before operational use, replace it with validated OIL-approved data and establish label definitions with domain experts.

## Known limitations

- One artifact models one target risk type. A production deployment can train one artifact per risk or add a multi-label orchestration layer outside this package.
- The severity thresholds are configurable only by changing the engine policy; they are not domain-calibrated OIL thresholds.
- Probabilities are not calibrated confidence scores.
- Formation/geological features are only useful if upstream data provides consistent point-in-time values.
- Temporal fallback without timestamps cannot guarantee protection against hidden ordering leakage.
- SHAP is intentionally not implemented here; M11 owns explainability.
- No synthetic oversampling is enabled by default because drilling records are sequential/time-dependent.
