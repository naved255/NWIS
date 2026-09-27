from nwis_decision_support import AlertContext

def test_probability_validation():
    try:
        AlertContext(well_id="W", risk_type="kick", probability=1.5, severity="high")
        assert False
    except Exception:
        assert True
