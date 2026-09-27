import numpy as np
import pandas as pd
from risk_engine.engine import RiskPredictionEngine
from risk_engine.schemas import TrainingConfig


def make_data(n=180):
    rng = np.random.default_rng(7)
    ts = pd.date_range("2025-01-01", periods=n, freq="h")
    torque = rng.normal(50, 8, n)
    pressure = rng.normal(300, 30, n)
    risk = np.where((torque > 57) & (pressure > 300), "torque_spike", "none")
    # Ensure both classes are present with a useful positive count.
    risk[:10] = "torque_spike"
    return pd.DataFrame({
        "timestamp": ts, "well_id": [f"W{i%6}" for i in range(n)],
        "depth": np.linspace(1000, 3000, n), "rop": rng.uniform(2, 12, n),
        "wob": rng.uniform(5, 30, n), "rpm": rng.uniform(60, 150, n),
        "torque": torque, "pressure": pressure, "mud_flow": rng.uniform(100, 300, n),
        "mud_weight": rng.uniform(9, 12, n), "formation": ["F1" if i%2 else "F2" for i in range(n)],
        "risk_type": risk,
    })


def test_train_save_load_predict(tmp_path):
    df = make_data()
    engine = RiskPredictionEngine(str(tmp_path / "artifact"))
    result = engine.fit(df, "torque_spike", TrainingConfig(model_type="hist_gradient_boosting", n_estimators=50))
    assert "precision" in result["test"]
    loaded = RiskPredictionEngine.load(str(tmp_path / "artifact"))
    pred = loaded.predict_risk(df.iloc[-1].drop(labels=["risk_type"]).to_dict())
    assert pred.risk_type == "torque_spike"
    assert 0 <= pred.probability <= 1
    assert pred.model_version == "1.0.0"
