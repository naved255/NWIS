import pandas as pd
from risk_engine.splitting import temporal_split


def test_temporal_split_is_ordered():
    df = pd.DataFrame({"timestamp": pd.date_range("2026-01-01", periods=20, freq="h"), "x": range(20)})
    tr, va, te = temporal_split(df, "timestamp", 0.2, 0.2)
    assert tr.timestamp.max() < va.timestamp.min()
    assert va.timestamp.max() < te.timestamp.min()
