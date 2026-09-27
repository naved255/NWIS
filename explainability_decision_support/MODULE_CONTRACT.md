# Module Contract

## A. SHAP

Input: trained tree model + exact model feature mapping.
Output: `ExplanationResult` with feature/value/contribution/direction and human explanation.

## B. Alerts

Input: `AlertContext` containing ML probability/severity plus any available depth, formation, historical and realtime anomaly evidence.
Output: `AlertResult`. `generated=false` means no configured rule matched.

## C. Recommendations

Input: `RecommendationContext` and evidence items supplied by existing NWIS services.
Output: `RecommendationResult`. If evidence is insufficient, `evidence_sufficient=false` and no specific operational procedure is invented.

## Ownership

This module does not own:

- model training
- historical retrieval
- PostGIS queries
- document ingestion
- realtime ingestion
- alert persistence
- UI rendering

Those remain in the existing NWIS modules.
