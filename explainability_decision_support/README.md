# NWIS Explainable AI & Decision Support

Standalone module for:

1. SHAP prediction explanations
2. Configurable risk alerts
3. Evidence-backed recommendations

This package does **not** access PostgreSQL, Qdrant, PostGIS, eRTMAC, or OIL systems directly. Integration is through small typed contracts/adapters so it can be dropped into the existing NWIS repository without coupling to unfinished modules.

## Architecture

```text
                 ML Prediction
                      |
              +-------+-------+
              |               |
              v               v
       SHAP Explainer     Alert Engine <---- context/evidence
              |               |
              v               v
        Explanation        Alert
              |               |
              +-------+-------+
                      |
                      v
             Recommendation Engine
                      |
          historical/evidence records
                      |
                      v
               Recommendation
```

## Installation

Core:

```bash
pip install -r requirements.txt
```

For SHAP tree explanations:

```bash
pip install shap lightgbm
```

For optional FastAPI routes:

```bash
pip install fastapi uvicorn
```

## Environment

Copy `.env.example` if desired. No secret is required by this package.

## Public functions

```python
from nwis_decision_support import (
    explain_prediction,
    generate_alert,
    generate_recommendation,
)
```

See `INTEGRATION.md` for integration with the existing NWIS services.
