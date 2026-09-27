from __future__ import annotations
import argparse
import json
import pandas as pd
from .engine import RiskPredictionEngine
from .schemas import TrainingConfig


def main():
    p = argparse.ArgumentParser(description="NWIS drilling risk engine")
    sub = p.add_subparsers(dest="command", required=True)
    t = sub.add_parser("train")
    t.add_argument("--csv", required=True)
    t.add_argument("--risk-type", required=True)
    t.add_argument("--artifact-dir", default="artifacts/risk_engine")
    t.add_argument("--model", choices=["lightgbm", "xgboost", "hist_gradient_boosting"], default="lightgbm")
    i = sub.add_parser("predict")
    i.add_argument("--artifact-dir", required=True)
    i.add_argument("--json", required=True)
    args = p.parse_args()
    if args.command == "train":
        engine = RiskPredictionEngine(args.artifact_dir)
        result = engine.fit(pd.read_csv(args.csv), args.risk_type, TrainingConfig(model_type=args.model))
        print(json.dumps(result, indent=2))
    else:
        engine = RiskPredictionEngine.load(args.artifact_dir)
        print(engine.predict_risk(json.loads(args.json)).model_dump_json(indent=2))

if __name__ == "__main__":
    main()
