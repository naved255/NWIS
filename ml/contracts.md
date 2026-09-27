# NWIS Risk Engine Contract

## Training input

A tabular dataset where each row represents a point-in-time drilling observation or a point-in-time engineered observation.

Required training fields:

- `risk_type`
- `timestamp` strongly recommended

Recommended identifiers:

- `well_id`

Recommended features:

`depth`, `rop`, `wob`, `rpm`, `torque`, `pressure`, `mud_flow`, `mud_weight`, `formation`, `inclination`, `azimuth`, `dogleg_severity`, `nearby_well_count`, `nearby_event_rate`, `historical_risk_rate`.

Additional numeric/categorical fields are accepted automatically.

## Prediction input

A JSON object under `features`. Missing known features are imputed by the persisted training pipeline; unknown extra fields are ignored.

## Prediction output

```json
{
  "risk_type": "stuck_pipe",
  "probability": 0.73,
  "severity": "high",
  "confidence": 0.82,
  "model_version": "1.0.0"
}
```

## Ownership boundary

- M10: model training, evaluation, persistence, inference.
- M11: SHAP/explainability.
- Geo module: nearby/offset calculations and trajectory-derived data.
- RAG module: historical semantic retrieval.
- Realtime module: eRTMAC ingestion/streaming.
- Alert/recommendation module: operational alerting and recommendations.
