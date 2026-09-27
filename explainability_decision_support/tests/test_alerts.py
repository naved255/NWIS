from nwis_decision_support import AlertContext, AlertRule, generate_alert
from nwis_decision_support.alerts.models import HistoricalEvidence, ParameterAnomaly

def test_high_alert_requires_history_and_depth():
    ctx = AlertContext(
        well_id="W-001", risk_type="stuck_pipe", probability=.82, severity="high", depth_m=2950,
        risk_interval_start_m=2900, risk_interval_end_m=3000,
        historical_evidence=[HistoricalEvidence(well_id="W-002", event_type="stuck_pipe", similarity=.84)],
    )
    result = generate_alert(ctx)
    assert result.generated is True
    assert result.severity == "high"
    assert result.evidence[0].well_id == "W-002"

def test_no_alert_without_required_evidence():
    ctx = AlertContext(well_id="W-001", risk_type="kick", probability=.80, severity="high", depth_m=2500)
    result = generate_alert(ctx)
    assert result.generated is False

def test_custom_anomaly_rule():
    ctx = AlertContext(
        well_id="W-001", risk_type="torque_spike", probability=.90, severity="critical",
        parameter_anomalies=[ParameterAnomaly(parameter="torque", value=20, baseline=12)],
    )
    rule = AlertRule(name="anomaly", min_probability=.85, require_parameter_anomaly=True, output_severity="critical")
    result = generate_alert(ctx, [rule])
    assert result.generated is True
    assert result.severity == "critical"
