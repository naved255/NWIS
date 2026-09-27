"""Minimal examples; SHAP example requires optional `shap` and a tree model."""
from nwis_decision_support import AlertContext, generate_alert
from nwis_decision_support.alerts.models import HistoricalEvidence

ctx = AlertContext(
    well_id="WELL-DEMO-001",
    risk_type="stuck_pipe",
    probability=0.81,
    severity="high",
    depth_m=2960,
    risk_interval_start_m=2900,
    risk_interval_end_m=3000,
    historical_evidence=[
        HistoricalEvidence(
            well_id="WELL-DEMO-002",
            event_type="stuck_pipe",
            similarity=0.87,
            depth_start_m=2920,
            depth_end_m=3010,
            summary="Synthetic example evidence only.",
        )
    ],
)
print(generate_alert(ctx).model_dump_json(indent=2))
