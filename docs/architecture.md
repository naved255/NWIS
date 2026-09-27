# NWIS Integrated Architecture

```text
Historical PDF/Image
      |
      v
Document Intelligence / OCR
      |
      v
NLP Extraction + Provenance
      |----------------------+
      v                      |
PostgreSQL/PostGIS       Vector Store
      |                      |
      +----> Geo ----------> RAG
                 \           /
                  \         /
                   v       v
                 ML Risk Prediction
                        |
                       SHAP
                        |
                     Alert
                        |
                 Recommendation
                        |
                    FastAPI
                        |
                    React UI

eRTMAC / Mock eRTMAC
        |
 Validation + Normalization
        |
 Anomaly classification
        |
 ML prediction callback
        |
 Alert/decision-support integration
        |
 WebSocket dashboard
```

The current repository is designed so external infrastructure (PostgreSQL/PostGIS, Qdrant, production eRTMAC, OCR engines) can be replaced by adapters for local integration testing.
