# NWIS Integration Guide

## 1. SHAP

The existing ML module should pass the **same feature vector used by the model** and the trained tree model to `explain_prediction()`.

```python
from nwis_decision_support import explain_prediction

result = explain_prediction(
    model=trained_model,
    features={
        "mud_weight": 1180.0,
        "pressure": 28500.0,
        "torque": 14.2,
        "rop": 8.5,
    },
    risk_type="stuck_pipe",
)
```

Do not pass post-processed or differently ordered features. SHAP must explain the exact model input.

## 2. Alerts

The ML service, geospatial service, and RAG service can independently construct an `AlertContext` and pass it to `generate_alert()`.

```python
from nwis_decision_support import AlertContext, generate_alert

alert = generate_alert(AlertContext(...))
```

No database write is performed by this package. The backend API should persist the returned alert using its existing Alert model/service.

## 3. Recommendations

Build evidence records from the existing RAG/geospatial/document services. The recommendation engine only cites evidence supplied to it.

```python
from nwis_decision_support import RecommendationContext, generate_recommendation

recommendation = generate_recommendation(RecommendationContext(...))
```

If no evidence meets the configured minimum, the output explicitly says evidence is insufficient rather than inventing an operational procedure.

## 4. Suggested NWIS flow

```text
nwis_ml
  -> PredictionResult
  -> explain_prediction()

geo_spatial + RAG + realtime
  -> AlertContext
  -> generate_alert()

RAG + Prediction + Alert evidence
  -> RecommendationContext
  -> generate_recommendation()

backend_api
  -> persist / expose results
```
